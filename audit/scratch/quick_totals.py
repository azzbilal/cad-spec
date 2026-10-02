import json
from pathlib import Path
for name in ['k3rwpbbk5sio4936onuai7ok','mk9qcuq2dsckzrf68gycyqls']:
 p=Path('results/training/run1/snapshots')/name
 rows=json.loads((p/'metrics.json').read_text())['metrics']
 print(name)
 for k in ['progress/rollouts','progress/input_tokens','progress/output_tokens','progress/tokens','time/step']:
  print(k,sum(r[k] for r in rows))
 for scope in ['all','effective']:
  for token in ['input','output','tokens']:
   k='train/agg/'+scope+'/num_'+(token+'_tokens' if token!='tokens' else 'tokens')+'/mean'
   print(k,sum(r['progress/rollouts']*(r['train/agg/all/is_trainable/mean'] if scope=='effective' else 1)*r.get(k,0) for r in rows))
 print('keys extra', [k for k in rows[0] if any(t in k for t in ['flat','group','train/','trainer','off_policy']) and not any(t in k for t in ['train/agg','train/cad-spec'])])
 print('usage',json.loads((p/'usage.json').read_text()))
 for r in rows:
  print(r['step'],r['progress/rollouts'], r['train/agg/all/is_trainable/mean'], r['train/agg/all/num_output_tokens/mean'], r['progress/tokens'], r['progress/input_tokens'], r['progress/output_tokens'])
