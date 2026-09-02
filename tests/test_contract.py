import hashlib
import json
import pytest

REV = "a" * 40
BASE = f"https://raw.githubusercontent.com/acme/grant-evidence/{REV}/grant-0"
AMOUNT = 10**15

def manifest(recipient, index=0):
    recipient_text = "0x" + recipient.hex() if isinstance(recipient, bytes) else str(recipient)
    return json.dumps({"grant_id":0,"milestone_index":index,"recipient":recipient_text,"revision":REV,"summary":"Published a working reproducible prototype with documented results.","deliverables":[{"name":"report","url":"https://example.org/report.pdf","sha256":"b"*64}]}, sort_keys=True, separators=(",", ":")).encode()

def deploy_grant(vm, deploy, sponsor, recipient, raw=None, count=1):
    vm.strict_mocks=True; vm.check_pickling=True
    with vm.prank(sponsor): c=deploy("contracts/GrantMilestoneEvidenceEscrow.py")
    raw = raw or manifest(recipient)
    plan=[]
    for i in range(count):
        item_raw = raw if i == 0 else manifest(recipient, i)
        plan.append({"amount_wei":AMOUNT,"deadline_seconds":3600*(i+1),"criteria":"A working prototype and reproducible report must be delivered.","manifest_sha256":hashlib.sha256(item_raw).hexdigest()})
    vm.value=AMOUNT*count
    recipient_text = "0x" + recipient.hex() if isinstance(recipient, bytes) else str(recipient)
    with vm.prank(sponsor): assert int(c.create_grant("Open climate tooling",recipient_text,BASE,REV,json.dumps(plan))) == 0
    vm.value=0
    return c, raw

def test_multitranche_happy_path_and_sequential_gate(direct_vm,direct_deploy,direct_alice,direct_bob):
    c,raw=deploy_grant(direct_vm,direct_deploy,direct_alice,direct_bob,count=2)
    with direct_vm.prank(direct_bob):
        assert c.claim_milestone(1)=="PREVIOUS_MILESTONE_NOT_PAID"
        assert c.claim_milestone(0)=="MILESTONE_CLAIMED"
        assert c.submit_milestone(0)=="MILESTONE_SUBMITTED"
    direct_vm.mock_web(BASE+r"/milestone-0\.json$",{"status":200,"body":raw})
    direct_vm.mock_llm(r"Decide whether this sponsor-committed.*",json.dumps({"criteria":"PASS"}))
    assert int(c.assess_milestone(0))==3
    with direct_vm.prank(direct_bob): assert c.pay_milestone(0)=="MILESTONE_PAID"
    with direct_vm.prank(direct_bob): assert c.claim_milestone(1)=="MILESTONE_CLAIMED"
    a=json.loads(c.get_accounting()); assert a["total_paid"]==str(AMOUNT); assert a["active_locked"]==str(AMOUNT)

def test_wrong_wallet_cannot_claim_pay_or_refund(direct_vm,direct_deploy,direct_alice,direct_bob,direct_charlie):
    c,_=deploy_grant(direct_vm,direct_deploy,direct_alice,direct_bob)
    before=c.get_milestone(0); accounting=c.get_accounting()
    with direct_vm.prank(direct_charlie):
        assert c.claim_milestone(0)=="RECIPIENT_ONLY"
        assert c.pay_milestone(0)=="MILESTONE_NOT_APPROVED"
        assert c.refund_expired_milestone(0)=="SPONSOR_ONLY"
    assert c.get_milestone(0)==before; assert c.get_accounting()==accounting

def test_digest_and_subject_binding_are_consequential(direct_vm,direct_deploy,direct_alice,direct_bob):
    raw=manifest(direct_bob)
    c,_=deploy_grant(direct_vm,direct_deploy,direct_alice,direct_bob,raw)
    with direct_vm.prank(direct_bob): c.claim_milestone(0); c.submit_milestone(0)
    forged=manifest(direct_alice)
    direct_vm.mock_web(BASE+r"/milestone-0\.json$",{"status":200,"body":forged})
    assert int(c.assess_milestone(0))==5
    result=json.loads(c.get_milestone(0)); diag=json.loads(result["diagnostics"])
    assert diag["digest"]=="FAIL" and result["amount_wei"]==str(AMOUNT)

def test_unavailable_freezes_and_retries(direct_vm,direct_deploy,direct_alice,direct_bob):
    c,raw=deploy_grant(direct_vm,direct_deploy,direct_alice,direct_bob)
    with direct_vm.prank(direct_bob): c.claim_milestone(0); c.submit_milestone(0)
    assert int(c.assess_milestone(0))==7
    assert json.loads(c.get_accounting())["active_locked"]==str(AMOUNT)
    direct_vm.mock_web(BASE+r"/milestone-0\.json$",{"status":200,"body":raw})
    direct_vm.mock_llm(r"Decide whether this sponsor-committed.*",json.dumps({"criteria":"PASS"}))
    assert int(c.assess_milestone(0))==3

def test_expiry_refund_only_sponsor_and_no_replay(direct_vm,direct_deploy,direct_alice,direct_bob,direct_charlie):
    direct_vm.warp("2026-09-02T00:00:00+00:00")
    c,_=deploy_grant(direct_vm,direct_deploy,direct_alice,direct_bob)
    direct_vm.warp("2026-09-02T01:00:01+00:00")
    with direct_vm.prank(direct_charlie): assert c.expire_milestone(0)=="MILESTONE_EXPIRED"
    with direct_vm.prank(direct_bob): assert c.refund_expired_milestone(0)=="SPONSOR_ONLY"
    with direct_vm.prank(direct_alice):
        assert c.refund_expired_milestone(0)=="EXPIRED_TRANCHE_REFUNDED"
        assert c.refund_expired_milestone(0)=="MILESTONE_NOT_EXPIRED"
    a=json.loads(c.get_accounting()); assert a["total_refunded"]==str(AMOUNT); assert a["active_locked"]=="0"

def test_invalid_payable_plan_reverts_without_records(direct_vm,direct_deploy,direct_alice,direct_bob):
    with direct_vm.prank(direct_alice): c=direct_deploy("contracts/GrantMilestoneEvidenceEscrow.py")
    direct_vm.value=AMOUNT
    bad=[{"amount_wei":AMOUNT-1,"deadline_seconds":3600,"criteria":"x","manifest_sha256":"b"*64}]
    with direct_vm.prank(direct_alice):
        with pytest.raises(Exception,match="DEPOSIT_PLAN_MISMATCH"): c.create_grant("x","0x"+direct_bob.hex(),BASE,REV,json.dumps(bad))
    direct_vm.value=0
    assert json.loads(c.get_counts())["grant_count"]==0
    assert json.loads(c.get_accounting())["total_deposited"]=="0"
