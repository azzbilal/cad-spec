"""Execute saved answers only via cad_spec.rubric.score, no inference."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if '--repo' in sys.argv:
    sys.path.insert(0, str(ROOT/'environments/cad_spec'))
os.environ.pop('CAD_SPEC_INPROC', None)
os.environ['CAD_SPEC_SANDBOX'] = 'reuse'
from cad_spec import measure, rubric, tasks

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', action='store_true')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    start = time.time()
    specs = {s.id:s for s in tasks.make_test_split()}
    work = []
    for label in ('base','adapter'):
        path = ROOT/f'results/training/run1/eval/{label}-test.jsonl'
        work.extend((label,json.loads(line)) for line in path.read_text(encoding='utf-8').splitlines() if '"tier":' in line)
    if not args.repo:
        work.reverse()  # Test order dependence with a fresh interpreter and reversed history.
    recs = []
    for i,(label,row) in enumerate(work):
        rep = rubric.score(row['completion'],specs[row['spec_id']])
        checks = {c.name:c.passed for c in rep.checks}
        rec = dict(arm=label,tier=row['tier'],spec_id=row['spec_id'],reward=rep.reward,
            binary_reward=int(rep.reward==1),checks=checks,details={c.name:c.detail for c in rep.checks},
            error=rep.error,parsed=rep.parsed,
            reward_equal=rep.reward==row['reward'],binary_equal=(rep.reward==1)==(row['reward']==1),
            checks_equal=checks==row['checks'],parsed_equal=rep.parsed==row['built'])
        recs.append(rec)
        if (i+1)%60==0:
            print(f'{args.out}: {i+1}/480',flush=True)
    measure.shutdown_worker()
    modules = {name:dict(path=mod.__file__,sha256=hashlib.sha256(Path(mod.__file__).read_bytes()).hexdigest())
               for name,mod in [('measure',measure),('rubric',rubric),('tasks',tasks)]}
    result = dict(python=sys.executable,version=sys.version,platform=platform.platform(),
        package_version=importlib.metadata.version('cad-spec'),scorer_version=rubric.SCORER_VERSION,
        cadquery=importlib.metadata.version('cadquery'),ocp=importlib.metadata.version('cadquery-ocp'),
        sandbox=measure.sandbox_info(),order='original' if args.repo else 'reversed',modules=modules,
        rows=len(recs),seconds=time.time()-start,
        mismatches=[r for r in recs if not all(r[k] for k in ('reward_equal','binary_equal','checks_equal','parsed_equal'))],
        counts={label:{'rows':sum(r['arm']==label for r in recs),'all_pass':sum(r['arm']==label and r['reward']==1 for r in recs)} for label in ('base','adapter')},
        results=recs)
    (ROOT/args.out).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2),flush=True)

if __name__=='__main__':
    main()
