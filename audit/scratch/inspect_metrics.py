import json
from pathlib import Path
p = Path('results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls')
x = json.loads((p/'metrics.json').read_text())
print('root', list(x), 'rows', len(x['metrics']), 'steps', [r['step'] for r in x['metrics']])
for r in x['metrics'][:1]:
    for k,v in r.items():
        if any(t in k for t in ['group','filter','progress/','batch/','num_output','num_input','trainable','off_policy','buffer','time/']): print(k,v)
for s in [12,34,38]:
    r = next(r for r in x['metrics'] if r['step']==s)
    print('STEP',s)
    for k,v in r.items():
        if 'L2' in k and any(t in k for t in ['reward/mean','turns/mean','trainable','filter','group','num_output']): print(k,v)
print('dist34', (p/'distributions-step-34.json').read_text())
