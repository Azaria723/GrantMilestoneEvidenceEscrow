"""Generate exact manifest bytes, digests, and Studio plan after a Git commit exists."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("--recipient",required=True)
p.add_argument("--repository",required=True,help="GitHub owner/repository containing the artifacts and manifests")
p.add_argument("--deliverable-revision",required=True)
p.add_argument("--grant-id",type=int,default=0)
p.add_argument("--output",default="evidence/grant-0")
args=p.parse_args()
if len(args.deliverable_revision)!=40 or any(c not in "0123456789abcdefABCDEF" for c in args.deliverable_revision): raise SystemExit("deliverable revision must be full 40-hex commit")
if len(args.recipient)!=42 or not args.recipient.startswith("0x"): raise SystemExit("recipient must be 0x address")
artifact_bytes=subprocess.check_output(['git','show',args.deliverable_revision+':docs/architecture.md'])
out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
criteria=["Document the protocol proof obligation and consensus binding matrix.","Document the protocol recovery rules."]
plan=[]
for i,text in enumerate(criteria):
 data={"fixture_notice":"Synthetic lifecycle test, not a claim of independently audited delivery.","grant_id":args.grant_id,"milestone_index":i,"recipient":args.recipient,"deliverable_revision":args.deliverable_revision.lower(),"summary":text,"deliverables":[{"name":f"milestone-{i}-report","url":f"https://raw.githubusercontent.com/{args.repository}/{args.deliverable_revision}/docs/architecture.md","sha256":hashlib.sha256(artifact_bytes).hexdigest()}]}
 raw=json.dumps(data,sort_keys=True,separators=(",", ":")).encode(); (out/f"milestone-{i}.json").write_bytes(raw)
 plan.append({"amount_wei":"1000000000000000","deadline_seconds":86400*(i+1),"criteria":text,"manifest_sha256":hashlib.sha256(raw).hexdigest()})
print(json.dumps(plan,separators=(",", ":")))
