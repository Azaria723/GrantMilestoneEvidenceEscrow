import hashlib
import json
import re
import pytest
import base64

REPO='acme/grant-evidence'
E='c'*40
D='a'*40
AMOUNT=10**15
ARTIFACT=b'Synthetic fixture: implementation and reproducible results.'
ARTIFACT_URL=f'https://raw.githubusercontent.com/{REPO}/{D}/report.txt'

def addr(v):
    return '0x'+v.hex() if isinstance(v,bytes) else str(v).lower()

def create(vm,deploy,sponsor,recipient,count=1):
    vm.strict_mocks=True
    vm.check_pickling=True
    vm.warp('2026-09-02T00:00:00+00:00')
    with vm.prank(sponsor): c=deploy('contracts/GrantMilestoneEvidenceEscrow.py')
    plan=[{'amount_wei':str(AMOUNT),'deadline_seconds':3600*(i+1),'criteria':'Deliver prototype and reproducible report.'} for i in range(count)]
    vm.value=AMOUNT*count
    with vm.prank(sponsor): assert c.create_grant('Future work',addr(recipient),REPO,json.dumps(plan))==0
    vm.value=0
    vm.deal(vm._contract_address,AMOUNT*count)
    vm.settlement_emissions=[]
    def emit_hook(context,request):
        if 'EthSend' in request:
            vm.settlement_emissions.append(request['EthSend']);return {'ok':None}
        raise AssertionError(f'Unexpected outbound operation: {request}')
    vm._gl_call_hook=emit_hook
    return c

PARENT='0x'+'a'*64
CHILD='0x'+'b'*64

def settlement_rpc(vm,caller,target,method='pay_milestone',milestone=0,attempt=1,credited=True,error=False):
    from genlayer.py import calldata
    parent={'hash':PARENT,'status':'FINALIZED','type':2,'value':0,'from_address':addr(caller),'to_address':addr(vm._contract_address),'data':{'calldata':base64.b64encode(calldata.encode({'method':method,'args':[milestone,attempt]})).decode()},'consensus_data':{'leader_receipt':[{'execution_result':'SUCCESS'}]},'triggered_transactions':[CHILD]}
    child={'hash':CHILD,'status':'FINALIZED','type':0,'value':AMOUNT,'from_address':addr(vm._contract_address),'to_address':addr(target),'triggered_by':PARENT,'value_credited':credited,'consensus_data':{'leader_receipt':[{'execution_result':'ERROR'}]} if error else None}
    vm.strict_mocks=False
    def handler(data):
        request=json.loads(data['body']);method_name=request['method'];params=request['params']
        result='0xf22f' if method_name=='eth_chainId' else parent if params==[PARENT] else child if params==[CHILD] else None
        return {'ok':{'response':{'status':200,'headers':{},'body':json.dumps({'id':1,'result':result}).encode()}}}
    vm._live_web_handler=handler

def pay_and_confirm(vm,c,caller,target,mid=0,attempt=1):
    with vm.prank(caller): assert c.pay_milestone(mid,attempt)=='SETTLEMENT_REQUESTED'
    emission=vm.settlement_emissions[-1];assert addr(emission['address']).lower()==addr(target).lower() and emission['value']==AMOUNT and emission['calldata']==b''
    settlement_rpc(vm,caller,target,milestone=mid,attempt=attempt)
    with vm.prank(caller): assert c.reconcile_settlement(mid,PARENT)=='MILESTONE_PAID'

def submit(vm,c,recipient,mid=0,nonce=1,changes=None,fetch=True,semantic='PASS'):
    data={'contract_address':addr(vm._contract_address),'chain_id':vm._chain_id,'grant_id':0,'milestone_id':mid,'milestone_index':mid,'recipient':addr(recipient),'submission_nonce':nonce,'deliverable_revision':D,'deliverables':[{'url':ARTIFACT_URL,'sha256':hashlib.sha256(ARTIFACT).hexdigest()}]}
    data.update(changes or {})
    raw=json.dumps(data,sort_keys=True).encode()
    with vm.prank(recipient): assert c.submit_milestone(mid,nonce,E,D,hashlib.sha256(raw).hexdigest())=='MILESTONE_SUBMITTED'
    record=json.loads(c.get_submission(mid,nonce))
    if fetch: vm.mock_web(re.escape(record['manifest_url'])+'$',{'status':200,'body':raw})
    if semantic is not None:
        vm.mock_web(re.escape(ARTIFACT_URL)+'$',{'status':200,'body':ARTIFACT})
        vm.mock_llm(r'Decide whether the actual fetched artifacts.*',json.dumps({'criteria':semantic}))
    return record,raw

def test_create_without_future_evidence_and_three_tranches(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=create(direct_vm,direct_deploy,direct_alice,direct_bob,3)
    assert json.loads(c.get_milestone(0))['manifest_url']==''
    with direct_vm.prank(direct_bob): assert c.claim_milestone(1)=='PREVIOUS_MILESTONE_NOT_PAID'
    for mid in range(3):
        with direct_vm.prank(direct_bob): assert c.claim_milestone(mid)=='MILESTONE_CLAIMED'
        record,raw=submit(direct_vm,c,direct_bob,mid,semantic='PASS' if mid==0 else None)
        assert E.encode() not in raw
        assert record['evidence_revision']==E and record['deliverable_revision']==D
        assert c.assess_milestone(mid,1)==3
        pay_and_confirm(direct_vm,c,direct_bob,direct_bob,mid)
        assert c.pay_milestone(mid,2)=='MILESTONE_NOT_APPROVED'
        assert c.expire_milestone(mid)=='MILESTONE_NOT_EXPIRABLE'
    a=json.loads(c.get_accounting())
    assert a['total_paid']==str(3*AMOUNT) and a['active_locked']=='0'

def test_permission_guards(direct_vm,direct_deploy,direct_alice,direct_bob,direct_charlie):
    c=create(direct_vm,direct_deploy,direct_alice,direct_bob)
    before=c.get_milestone(0),c.get_accounting()
    for actor in [direct_alice,direct_charlie]:
        with direct_vm.prank(actor):
            assert c.claim_milestone(0)=='RECIPIENT_ONLY'
            assert c.submit_milestone(0,1,E,D,'b'*64)=='RECIPIENT_ONLY'
    with direct_vm.prank(direct_charlie): assert c.refund_expired_milestone(0,1)=='SPONSOR_ONLY'
    assert before==(c.get_milestone(0),c.get_accounting())

@pytest.mark.parametrize('field,value',[('contract_address','0x'+'1'*40),('chain_id',123456),('grant_id',9),('milestone_id',9),('milestone_index',9),('submission_nonce',9),('recipient','0x'+'1'*40),('deliverable_revision','d'*40)])
def test_valid_hash_wrong_binding(direct_vm,direct_deploy,direct_alice,direct_bob,field,value):
    c=create(direct_vm,direct_deploy,direct_alice,direct_bob)
    with direct_vm.prank(direct_bob): c.claim_milestone(0)
    submit(direct_vm,c,direct_bob,changes={field:value},semantic=None)
    assert c.assess_milestone(0,1)==5
    diag=json.loads(c.get_assessment(0,1,1))
    assert diag['digest']=='PASS' and diag['binding']=='FAIL'
    assert c.pay_milestone(0,1)=='MILESTONE_NOT_APPROVED'

def test_correction_append_only_and_stale_nonce(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=create(direct_vm,direct_deploy,direct_alice,direct_bob)
    with direct_vm.prank(direct_bob): c.claim_milestone(0)
    submit(direct_vm,c,direct_bob,changes={'submission_nonce':999},semantic=None)
    assert c.assess_milestone(0,1)==5
    old=c.get_submission(0,1),c.get_assessment(0,1,1)
    with direct_vm.prank(direct_bob): assert c.submit_milestone(0,1,E,D,'b'*64)=='STALE_SUBMISSION_NONCE'
    submit(direct_vm,c,direct_bob,nonce=2)
    before=c.get_milestone(0)
    assert c.assess_milestone(0,1)=='STALE_SUBMISSION_NONCE'
    assert c.get_milestone(0)==before
    assert c.assess_milestone(0,2)==3
    assert old==(c.get_submission(0,1),c.get_assessment(0,1,1))
    with direct_vm.prank(direct_bob): assert c.submit_milestone(0,3,E,D,'b'*64)=='MILESTONE_NOT_SUBMITTABLE'

def test_unavailable_retry_review_grace_and_approved_protection(direct_vm,direct_deploy,direct_alice,direct_bob):
    c=create(direct_vm,direct_deploy,direct_alice,direct_bob)
    with direct_vm.prank(direct_bob): c.claim_milestone(0)
    record,raw=submit(direct_vm,c,direct_bob,fetch=False,semantic=None)
    assert c.assess_milestone(0,1)==7
    old=c.get_assessment(0,1,1)
    direct_vm.warp('2026-09-02T01:00:01+00:00')
    assert c.expire_milestone(0)=='DEADLINE_NOT_PASSED'
    with direct_vm.prank(direct_alice): assert c.refund_expired_milestone(0,1)=='MILESTONE_NOT_EXPIRED'
    direct_vm.mock_web(re.escape(record['manifest_url'])+'$',{'status':200,'body':raw})
    direct_vm.mock_web(re.escape(ARTIFACT_URL)+'$',{'status':200,'body':ARTIFACT})
    direct_vm.mock_llm(r'Decide whether the actual fetched artifacts.*','{"criteria":"PASS"}')
    assert c.assess_milestone(0,1)==3
    assert c.get_assessment(0,1,1)==old
    assert json.loads(c.get_submission(0,1))['assessment_count']==2
    direct_vm.warp('2026-09-04T00:00:00+00:00')
    assert c.expire_milestone(0)=='MILESTONE_NOT_EXPIRABLE'
    pay_and_confirm(direct_vm,c,direct_bob,direct_bob)

def test_review_cutoff_refund_late_assessment(direct_vm,direct_deploy,direct_alice,direct_bob,direct_charlie):
    c=create(direct_vm,direct_deploy,direct_alice,direct_bob)
    with direct_vm.prank(direct_bob): c.claim_milestone(0)
    submit(direct_vm,c,direct_bob,fetch=False,semantic=None)
    direct_vm.warp('2026-09-03T01:00:00+00:00')
    assert c.expire_milestone(0)=='DEADLINE_NOT_PASSED'
    direct_vm.warp('2026-09-03T01:00:01+00:00')
    assert c.assess_milestone(0,1)=='REVIEW_WINDOW_CLOSED'
    assert c.expire_milestone(0)=='MILESTONE_EXPIRED'
    with direct_vm.prank(direct_charlie): assert c.refund_expired_milestone(0,1)=='SPONSOR_ONLY'
    with direct_vm.prank(direct_alice):
        assert c.refund_expired_milestone(0,1)=='SETTLEMENT_REQUESTED'
    settlement_rpc(direct_vm,direct_alice,direct_alice,method='refund_expired_milestone')
    with direct_vm.prank(direct_alice):
        assert c.reconcile_settlement(0,PARENT)=='EXPIRED_TRANCHE_REFUNDED'
        assert c.refund_expired_milestone(0,2)=='MILESTONE_NOT_EXPIRED'
    assert c.assess_milestone(0,1)=='MILESTONE_NOT_ASSESSABLE'
    assert c.pay_milestone(0,1)=='MILESTONE_NOT_APPROVED'
    assert json.loads(c.get_accounting())['active_locked']=='0'

@pytest.mark.parametrize('url',['https://attacker.example/a.txt',f'https://raw.githubusercontent.com/{REPO}/{D}/../bad.txt',f'https://raw.githubusercontent.com/{REPO}/{D}/report.txt?x=1'])
def test_source_policy(direct_vm,direct_deploy,direct_alice,direct_bob,url):
    c=create(direct_vm,direct_deploy,direct_alice,direct_bob)
    with direct_vm.prank(direct_bob): c.claim_milestone(0)
    submit(direct_vm,c,direct_bob,changes={'deliverables':[{'url':url,'sha256':'b'*64}]},semantic=None)
    assert c.assess_milestone(0,1)==5
    assert 'ARTIFACT_SOURCE_POLICY_MISMATCH' in c.get_assessment(0,1,1)

@pytest.mark.parametrize('response,expected',[('changed',5),('oversized',7),('missing',7)])
def test_artifact_acquisition(direct_vm,direct_deploy,direct_alice,direct_bob,response,expected):
    c=create(direct_vm,direct_deploy,direct_alice,direct_bob)
    with direct_vm.prank(direct_bob): c.claim_milestone(0)
    submit(direct_vm,c,direct_bob,semantic=None)
    direct_vm.mock_web(re.escape(ARTIFACT_URL)+'$',{'status':404 if response=='missing' else 200,'body':b'x'*30001 if response=='oversized' else b'changed'})
    assert c.assess_milestone(0,1)==expected
    assert json.loads(c.get_accounting())['active_locked']==str(AMOUNT)

@pytest.mark.parametrize('verdict,expected',[('FAIL',5),('UNRESOLVED',7),('PAY_NOW',7)])
def test_semantic_result_bounded(direct_vm,direct_deploy,direct_alice,direct_bob,verdict,expected):
    c=create(direct_vm,direct_deploy,direct_alice,direct_bob)
    with direct_vm.prank(direct_bob): c.claim_milestone(0)
    submit(direct_vm,c,direct_bob,semantic=verdict)
    assert c.assess_milestone(0,1)==expected
    assert c.pay_milestone(0,1)=='MILESTONE_NOT_APPROVED'

def test_invalid_payable_plan(direct_vm,direct_deploy,direct_alice,direct_bob):
    with direct_vm.prank(direct_alice): c=direct_deploy('contracts/GrantMilestoneEvidenceEscrow.py')
    direct_vm.value=AMOUNT
    with direct_vm.prank(direct_alice):
        with pytest.raises(Exception,match='DEPOSIT_PLAN_MISMATCH'):
            c.create_grant('Mismatch',addr(direct_bob),REPO,json.dumps([{'amount_wei':'1','deadline_seconds':3600,'criteria':'Deliver report'}]))
    direct_vm.value=0
    assert json.loads(c.get_counts())['grant_count']==0
    assert json.loads(c.get_accounting())['total_deposited']=='0'

@pytest.mark.parametrize('change,reason',[
    ({'amount_wei':1},'INVALID_AMOUNT'),
    ({'amount_wei':'1.5'},'INVALID_AMOUNT'),
    ({'deadline_seconds':300.5},'INVALID_TERMS_TYPES'),
    ({'deadline_seconds':True},'INVALID_TERMS_TYPES'),
    ({'criteria':{}},'INVALID_TERMS_TYPES'),
])
def test_plan_types_revert(direct_vm,direct_deploy,direct_alice,direct_bob,change,reason):
    with direct_vm.prank(direct_alice): c=direct_deploy('contracts/GrantMilestoneEvidenceEscrow.py')
    direct_vm.value=AMOUNT
    item={'amount_wei':str(AMOUNT),'deadline_seconds':3600,'criteria':'Deliver report'}
    item.update(change)
    with direct_vm.prank(direct_alice):
        with pytest.raises(Exception,match=reason): c.create_grant('Invalid',addr(direct_bob),REPO,json.dumps([item]))
    direct_vm.value=0
    assert json.loads(c.get_counts())['grant_count']==0

def test_plan_sum_overflow_reverts(direct_vm,direct_deploy,direct_alice,direct_bob):
    with direct_vm.prank(direct_alice): c=direct_deploy('contracts/GrantMilestoneEvidenceEscrow.py')
    direct_vm.value=AMOUNT
    plan=[{'amount_wei':str(2**255),'deadline_seconds':3600*(i+1),'criteria':'Deliver report'} for i in range(2)]
    with direct_vm.prank(direct_alice):
        with pytest.raises(Exception,match='PLAN_AMOUNT_OVERFLOW'): c.create_grant('Overflow',addr(direct_bob),REPO,json.dumps(plan))
    direct_vm.value=0
    assert json.loads(c.get_accounting())['total_deposited']=='0'

@pytest.mark.parametrize('fault',['wrong-chain','wrong-parent','wrong-method','wrong-milestone','wrong-attempt','wrong-target','wrong-amount','internal-call','uncredited','missing-credit','child-error','unlinked'])
def test_forged_or_incomplete_settlement_never_marks_paid(direct_vm,direct_deploy,direct_alice,direct_bob,fault):
    vm=direct_vm;c=create(vm,direct_deploy,direct_alice,direct_bob)
    from genlayer.py import calldata as settlement_calldata
    with vm.prank(direct_bob): c.claim_milestone(0)
    submit(vm,c,direct_bob);assert c.assess_milestone(0,1)==3
    with vm.prank(direct_bob): assert c.pay_milestone(0,1)=='SETTLEMENT_REQUESTED'
    settlement_rpc(vm,direct_bob,direct_bob)
    original=vm._live_web_handler
    def altered(data):
        response=original(data);payload=json.loads(response['ok']['response']['body']);req=json.loads(data['body']);result=payload['result']
        if req['method']=='eth_chainId' and fault=='wrong-chain':
            payload['result']='0x1';response['ok']['response']['body']=json.dumps(payload).encode();return response
        elif req['method']=='eth_getTransactionByHash' and req['params']==[PARENT]:
            if fault=='wrong-parent': result['from_address']='0x'+'1'*40
            if fault in ['wrong-method','wrong-milestone','wrong-attempt']:
                call={'method':'other' if fault=='wrong-method' else 'pay_milestone','args':[1 if fault=='wrong-milestone' else 0,2 if fault=='wrong-attempt' else 1]}
                result['data']['calldata']=base64.b64encode(settlement_calldata.encode(call)).decode()
            if fault=='unlinked': result['triggered_transactions']=[]
        elif req['method']=='eth_getTransactionByHash' and req['params']==[CHILD]:
            if fault=='wrong-target': result['to_address']=addr(direct_alice)
            if fault=='wrong-amount': result['value']=1
            if fault=='internal-call': result['type']=2
            if fault=='uncredited': result['value_credited']=False
            if fault=='missing-credit': result.pop('value_credited')
            if fault=='child-error': result['consensus_data']={'leader_receipt':[{'execution_result':'ERROR'}]}
        payload['result']=result;response['ok']['response']['body']=json.dumps(payload).encode();return response
    vm._live_web_handler=altered
    before=c.get_accounting()
    with vm.prank(direct_bob): assert c.reconcile_settlement(0,PARENT)=='SETTLEMENT_UNRESOLVED'
    state=json.loads(c.get_milestone(0));assert state['status']==3 and state['amount_wei']==str(AMOUNT) and state['settlement_state']==1
    assert c.get_accounting()==before

def test_failed_transfer_is_retryable_but_does_not_clear_amount(direct_vm,direct_deploy,direct_alice,direct_bob):
    vm=direct_vm;c=create(vm,direct_deploy,direct_alice,direct_bob)
    with vm.prank(direct_bob): c.claim_milestone(0)
    submit(vm,c,direct_bob);assert c.assess_milestone(0,1)==3
    with vm.prank(direct_bob): assert c.pay_milestone(0,1)=='SETTLEMENT_REQUESTED'
    settlement_rpc(vm,direct_bob,direct_bob,credited=False,error=True)
    with vm.prank(direct_bob): assert c.reconcile_settlement(0,PARENT)=='SETTLEMENT_FAILED_RETRYABLE'
    state=json.loads(c.get_milestone(0));assert state['status']==3 and state['amount_wei']==str(AMOUNT) and state['settlement_state']==3
    assert json.loads(c.get_accounting())['total_paid']=='0'
    vm.deal(vm._contract_address,0)
    with vm.prank(direct_bob): assert c.pay_milestone(0,2)=='SETTLEMENT_RESERVE_SHORTFALL'

def test_emit_failure_rolls_back_pending_state(direct_vm,direct_deploy,direct_alice,direct_bob):
    vm=direct_vm;c=create(vm,direct_deploy,direct_alice,direct_bob)
    with vm.prank(direct_bob): c.claim_milestone(0)
    submit(vm,c,direct_bob);assert c.assess_milestone(0,1)==3
    vm._gl_call_hook=lambda context,request: (_ for _ in ()).throw(RuntimeError('SIMULATED_SEND_FAILURE'))
    before=c.get_milestone(0),c.get_accounting()
    with vm.prank(direct_bob),pytest.raises(Exception): c.pay_milestone(0,1)
    assert before==(c.get_milestone(0),c.get_accounting())
