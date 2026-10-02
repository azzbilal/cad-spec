import csv,json
from pathlib import Path
from statistics import mean
out=Path('audit')
d=json.loads((out/'reconstruction.json').read_text(encoding='utf-8'))
rows=list(csv.DictReader((out/'run-steps.csv').open(encoding='utf-8')))
result={}
alpha=d['summaries']['run']['alpha']
for x in ['L4','L2','L1-L3']:
 i=sum(int(r[x+'_discard_input']) for r in rows)
 o=sum(int(r[x+'_discard_output']) for r in rows)
 result[x]=dict(discard_input=i,discard_output=o,list_cost=(.2*i+.6*o)/1e6,allocated_cost=alpha*(.2*i+.6*o)/1e6)
result['discard_total']=sum(v['allocated_cost'] for v in result.values())
result['frozen_smoke_prediction']=38*.13208
result['frozen_smoke_error_pct']=(38*.13208/13.8721-1)*100
result['share_only_smoke_length_error_pct']=(d['fixed_smoke_lengths_run_prediction']/13.8721-1)*100
# Compare conservative length-aware model to a declared per-step allocation proxy.
eta=d['pooled_token_overhead_factor']
tail=d['summaries']['run']['unassigned_cost']/38
errors=[float(r['list_training'])+eta*float(r['list_inference'])-(float(r['allocated_cost'])+tail) for r in rows]
result['proxy_errors_38']=dict(mae=mean(abs(v) for v in errors),rmse=mean(v*v for v in errors)**.5,min=min(errors),max=max(errors))
smoke=d['summaries']['smoke']['usage'];run=d['summaries']['run']['usage']
result['inferred_input_rates_if_output_full_list']={k:(v['inference']['cost_usd']-.6*v['inference']['output_tokens']/1e6)/(v['inference']['input_tokens']/1e6) for k,v in [('smoke',smoke),('run',run)]}
result['reconciliation']={}
for k in ['smoke','run']:
 u=d['summaries'][k]['usage'];s=d['summaries'][k]
 list_inf=(.2*u['inference']['input_tokens']+.6*u['inference']['output_tokens'])/1e6
 result['reconciliation'][k]=dict(list_inference=list_inf,shortfall=list_inf-u['inference']['cost_usd'],
   inference_overhead_input=u['inference']['input_tokens']/s['sums']['gen_input'],
   inference_overhead_output=u['inference']['output_tokens']/s['sums']['gen_output'])
result['timestamps']={}
metrics=json.loads(Path('results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls/metrics.json').read_text(encoding='utf-8'))['metrics']
for m in metrics:
 if m['step'] in [12,13,17,21,24,26,28,30,32,33,34,35,36,38]:result['timestamps'][m['step']]=m['timestamp']
(out/'extra-analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
patches=[]
for candidate,target in [('spend_guard_candidate.py','scripts/train_spend_guard.py'),('preflight_candidate.py','scripts/training_cost_preflight.py')]:
 text=(out/'scratch'/candidate).read_text(encoding='utf-8')
 patches.append('diff --git a/'+target+' b/'+target+'\nnew file mode 100644\n--- /dev/null\n+++ b/'+target+'\n@@ -0,0 +1,'+str(len(text.splitlines()))+' @@\n'+''.join('+'+line+'\n' for line in text.splitlines()))
(out/'guardrails-proposed.patch').write_text('\n'.join(patches),encoding='utf-8')
