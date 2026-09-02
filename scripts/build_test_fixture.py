"""Print a synthetic manifest for a deployed grant; does not upload or overwrite files.

Commit artifact D first. Save stdout as the exact UTF-8 manifest path printed to
stderr, commit it as E, then hash those saved bytes and submit E/D/hash on-chain.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys

p = argparse.ArgumentParser()
p.add_argument('--contract', required=True)
p.add_argument('--chain-id', type=int, default=61999)
p.add_argument('--recipient', required=True)
p.add_argument('--repository', required=True)
p.add_argument('--deliverable-revision', required=True)
p.add_argument('--artifact', default='docs/architecture.md')
p.add_argument('--grant-id', type=int, required=True)
p.add_argument('--milestone-id', type=int, required=True)
p.add_argument('--milestone-index', type=int, required=True)
p.add_argument('--nonce', type=int, required=True)
args = p.parse_args()
for address in [args.contract, args.recipient]:
    if not re.fullmatch(r'0x[0-9a-fA-F]{40}', address): p.error('Invalid address')
if not re.fullmatch(r'[0-9a-fA-F]{40}', args.deliverable_revision): p.error('Use full commit D')
for path in [args.repository, args.artifact]:
    if any(not re.fullmatch(r'[A-Za-z0-9_.-]+', s) or s in ['.', '..'] for s in path.split('/')): p.error('Unsafe repository/artifact path')
if len(args.repository.split('/')) != 2: p.error('Use owner/repository')
if min(args.chain_id,args.grant_id,args.milestone_id,args.milestone_index) < 0 or not 1 <= args.nonce <= 8: p.error('Invalid identity numbers')
revision = args.deliverable_revision.lower()
body = subprocess.check_output(['git', 'show', revision + ':' + args.artifact])
body.decode('utf-8')
if len(body) > 30000: p.error('Artifact exceeds 30 KB')
record = {
    'fixture_notice': 'Synthetic lifecycle fixture, not independent delivery or authorship proof.',
    'contract_address': args.contract.lower(), 'chain_id': args.chain_id,
    'grant_id': args.grant_id, 'milestone_id': args.milestone_id,
    'milestone_index': args.milestone_index, 'recipient': args.recipient.lower(),
    'submission_nonce': args.nonce, 'deliverable_revision': revision,
    'deliverables': [{'url': f'https://raw.githubusercontent.com/{args.repository}/{revision}/{args.artifact}', 'sha256': hashlib.sha256(body).hexdigest()}],
}
raw = json.dumps(record, sort_keys=True, separators=(',', ':')).encode('utf-8')
sys.stdout.buffer.write(raw)
print(f'\nPath: evidence/grant-{args.grant_id}/milestone-{args.milestone_index}/submission-{args.nonce}.json', file=sys.stderr)
print('SHA256 of stdout bytes (no trailing newline): ' + hashlib.sha256(raw).hexdigest(), file=sys.stderr)
