"""Generate exact manifest bytes, digests, and Studio plan after a Git commit exists."""
import argparse
import hashlib
import json
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("--recipient",required=True)
p.add_argument("--revision",required=True)
p.add_argument("--grant-id",type=int,default=0)
p.add_argument("--output",default="evidence/grant-0")
args=p.parse_args()
if len(args.revision)!=40 or any(c not in "0123456789abcdefABCDEF" for c in args.revision): raise SystemExit("revision must be full 40-hex commit")
if len(args.recipient)!=42 or not args.recipient.startswith("0x"): raise SystemExit("recipient must be 0x address")
out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
criteria=["Publish a working prototype and a reproducible delivery report.","Publish an independent evaluation and final operations guide."]
plan=[]
for i,text in enumerate(criteria):
 data={"grant_id":args.grant_id,"milestone_index":i,"recipient":args.recipient,"revision":args.revision.lower(),"summary":text,"deliverables":[{"name":f"milestone-{i}-report","url":f"https://github.com/Azaria723/GrantMilestoneEvidenceEscrow/blob/{args.revision}/docs/architecture.md","sha256":hashlib.sha256(Path("docs/architecture.md").read_bytes()).hexdigest()}]}
 raw=json.dumps(data,sort_keys=True,separators=(",", ":")).encode(); (out/f"milestone-{i}.json").write_bytes(raw)
 plan.append({"amount_wei":"1000000000000000","deadline_seconds":86400*(i+1),"criteria":text,"manifest_sha256":hashlib.sha256(raw).hexdigest()})
print(json.dumps(plan,separators=(",", ":")))
