"""Offline reconstruction only. No API calls, training, or evaluation.

Run from repo root: python audit/scratch/reconstruct_cost.py
"""
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
SNAP = ROOT / 'results/training/run1/snapshots'
OUT = ROOT / 'audit'
IDS = {'smoke': 'k3rwpbbk5sio4936onuai7ok', 'run': 'mk9qcuq2dsckzrf68gycyqls'}
ENVS = ['L4', 'L2', 'L1-L3']

def integer(x):
    assert math.isclose(x, round(x), abs_tol=1e-7), x
    return round(x)

def parse(label, run_id):
    folder = SNAP / run_id
    manifest = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        data = (folder/item['file']).read_bytes()
        assert len(data) == item['bytes']
        assert hashlib.sha256(data).hexdigest() == item['sha256']
    metrics = json.loads((folder/'metrics.json').read_text(encoding='utf-8'))['metrics']
    usage = json.loads((folder/'usage.json').read_text(encoding='utf-8'))
    alpha = usage['inference']['cost_usd'] / (
        .2*usage['inference']['input_tokens']/1e6 + .6*usage['inference']['output_tokens']/1e6)
    rows = []
    for m in metrics:
        n = integer(m['progress/rollouts'])
        e = integer(n*m['train/agg/all/is_trainable/mean'])
        assert e == 128
        assert integer(n*m['pre_filters/all/dropped_rate']) == n-e
        assert math.isclose(m['pre_filters/all/dropped_rate'],m['train/agg/all/filters/zero_advantage/mean'])
        assert m['train/agg/effective/filters/zero_advantage/mean'] == 0
        assert m['train/agg/all/has_error/mean'] == 0
        r = dict(run=label,step=m['step'],generated=n,trained=e,share=e/n,
                 truncation=m['train/agg/all/is_truncated/mean'],duration_s=m['time/step'],
                 gen_input=integer(n*m['train/agg/all/num_input_tokens/mean']),
                 gen_output=integer(n*m['train/agg/all/num_output_tokens/mean']),
                 trained_tokens=integer(m['progress/input_tokens']+m['progress/output_tokens']),
                 input_mean=m['train/agg/all/num_input_tokens/mean'],
                 output_mean=m['train/agg/all/num_output_tokens/mean'])
        assert r['gen_input']+r['gen_output'] == integer(m['progress/tokens'])
        for env in ENVS:
            prefix='train/cad-spec-'+env
            count=integer(n*(m['batch/cad-spec-'+env] or 0))
            effective=integer(count*(m[prefix+'/all/is_trainable/mean'] or 0))
            all_reward=count*(m[prefix+'/all/reward/mean'] or 0)
            effective_reward=effective*(m[prefix+'/effective/reward/mean'] or 0)
            solved=integer((all_reward-effective_reward)/8)
            flat=integer((count-effective)/8)
            assert 0 <= solved <= flat
            r[env+'_generated']=count
            r[env+'_trained']=effective
            r[env+'_solved']=solved
            r[env+'_failed']=flat-solved
            r[env+'_output_mean']=m[prefix+'/all/num_output_tokens/mean'] or 0
            r[env+'_truncation']=m[prefix+'/all/is_truncated/mean']
            r[env+'_discard_input']=integer(count*(m[prefix+'/all/num_input_tokens/mean'] or 0)-effective*(m[prefix+'/effective/num_input_tokens/mean'] or 0))
            r[env+'_discard_output']=integer(count*(m[prefix+'/all/num_output_tokens/mean'] or 0)-effective*(m[prefix+'/effective/num_output_tokens/mean'] or 0))
        assert sum(r[x+'_generated'] for x in ENVS)==n
        assert sum(r[x+'_trained'] for x in ENVS)==e
        path=folder/('distributions-step-'+str(m['step'])+'.json')
        try:
            d=json.loads(path.read_text(encoding='utf-8'))
            r['distribution']='ok'
            assert sum(x['count'] for x in d['bins']['rewards']) == e
            r['trained_zero_rewards']=d['bins']['rewards'][0]['count']
            r['trained_one_rewards']=d['bins']['rewards'][-1]['count']
        except json.JSONDecodeError:
            assert 'HTTP 429' in path.read_text(encoding='utf-8')
            assert next(x for x in manifest['files'] if x['file']==path.name)['exit_code']==1
            r['distribution']='429'
            r['trained_zero_rewards']=r['trained_one_rewards']=None
        r['list_inference']= (.2*r['gen_input']+.6*r['gen_output'])/1e6
        r['list_training']=.6*r['trained_tokens']/1e6
        r['allocated_cost']=r['list_training']+alpha*r['list_inference']
        r['list_cost']=r['list_training']+r['list_inference']
        rows.append(r)
    assert sum(r['trained_tokens'] for r in rows)==usage['training']['tokens']
    sums={k:sum(r[k] for r in rows) for k in ['generated','trained','gen_input','gen_output','trained_tokens','list_inference','list_training','allocated_cost','duration_s']}
    summary=dict(alpha=alpha,usage=usage,sums=sums,
                 unassigned_input=usage['inference']['input_tokens']-sums['gen_input'],
                 unassigned_output=usage['inference']['output_tokens']-sums['gen_output'],
                 unassigned_cost=usage['total_cost_usd']-sums['allocated_cost'])
    return rows,summary

def phase(rows):
    n=sum(r['generated'] for r in rows); e=sum(r['trained'] for r in rows)
    return dict(steps=len(rows),generated_per_step=n/len(rows),share=e/n,
        output_mean=sum(r['gen_output'] for r in rows)/n,
        input_mean=sum(r['gen_input'] for r in rows)/n,
        trained_tokens_per_answer=sum(r['trained_tokens'] for r in rows)/e,
        seconds=mean(r['duration_s'] for r in rows),cost=mean(r['allocated_cost'] for r in rows),
        list_cost=mean(r['list_cost'] for r in rows),
        env={x:dict(generated=sum(r[x+'_generated'] for r in rows),trained=sum(r[x+'_trained'] for r in rows),solved=sum(r[x+'_solved'] for r in rows),failed=sum(r[x+'_failed'] for r in rows),
                   output_mean=sum(r[x+'_output_mean']*r[x+'_generated'] for r in rows)/sum(r[x+'_generated'] for r in rows)) for x in ENVS})

def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])

def main():
    allrows={}; summaries={}
    for label,run_id in IDS.items():
        rows,s=parse(label,run_id);allrows[label]=rows;summaries[label]=s
        with (OUT/(label+'-steps.csv')).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    run=allrows['run']; smoke=allrows['smoke']
    phases={'smoke 1-5':phase(smoke)}
    for name,a,b in [('run 1-5',1,5),('run 6-14',6,14),('run 15-24',15,24),('run 17-28',17,28),('run 25-32',25,32),('run 33-38',33,38),('run 1-38',1,38)]:
        phases[name]=phase([r for r in run if a<=r['step']<=b])
    # Symmetric decomposition: inference N times per-answer price; training separately.
    s=phases['smoke 1-5']; l=phases['run 33-38']
    ns,nl=s['generated_per_step'],l['generated_per_step']
    vs=(.2*s['input_mean']+.6*s['output_mean'])/1e6
    vl=(.2*l['input_mean']+.6*l['output_mean'])/1e6
    decomposition=dict(volume=(nl-ns)*(vl+vs)/2,
         output_length=.6*(l['output_mean']-s['output_mean'])/1e6*(nl+ns)/2,
         input_length=.2*(l['input_mean']-s['input_mean'])/1e6*(nl+ns)/2,
         training_length=.6*128*(l['trained_tokens_per_answer']-s['trained_tokens_per_answer'])/1e6,
         early_list=s['list_cost'],late_list=l['list_cost'])
    # A smoke-calibrated forecast with observed f and lengths is a retrospective model,
    # not an independent validation: overhead allocated equally as a declared convention.
    eta=sum((x['usage']['inference']['input_tokens']+x['usage']['inference']['output_tokens']) for x in summaries.values())/sum(x['sums']['gen_input']+x['sums']['gen_output'] for x in summaries.values())
    errs={}
    for label,rows in allrows.items():
        predicted=sum(r['list_training']+eta*r['list_inference'] for r in rows)
        actual=summaries[label]['usage']['total_cost_usd']
        errs[label]=dict(predicted=predicted,actual=actual,error=predicted-actual,percent=(predicted/actual-1)*100)
    # Baseline per-answer cost frozen at smoke, using observed shares only.
    predicted_fixed=sum(.6*128*s['trained_tokens_per_answer']/1e6 + eta*r['generated']*vs for r in run)
    lines=['## Reconstructed steps','',
        'Flat groups are `all-solved/all-failed`. Output means use all generated answers. Truncation uses all generated answers. Flat counts are algebraically reconstructed from aggregate binary rewards, not raw group vectors. `429` means the distribution capture failed.','',
        table(['Step','Generated','Trained','Share','L4 flat S/F','L2 flat S/F','L1-L3 flat S/F','Output mean L4/L2/L1-L3','Trunc %','Seconds','Dist'],[
        [r['step'],r['generated'],r['trained'],f"{r['share']:.1%}",*[str(r[x+'_solved'])+'/'+str(r[x+'_failed']) for x in ENVS],'/'.join(f"{r[x+'_output_mean']:.1f}" if r[x+'_generated'] else 'n/a' for x in ENVS),f"{100*r['truncation']:.2f}",f"{r['duration_s']:.1f}",r['distribution']] for r in run]),'',
        '## Step cost attribution','',
        'These are estimates for completed-step cohorts, not per-step invoices. Training token pricing is exact before four-decimal usage rounding; inference applies the run-level billing/list ratio uniformly. The unassigned tail remains separate.','',
        table(['Step','Generated input','Generated output','Trained tokens','Training $','Inference list $','Allocated total $'],[
        [r['step'],r['gen_input'],r['gen_output'],r['trained_tokens'],f"{r['list_training']:.4f}",f"{r['list_inference']:.4f}",f"{r['allocated_cost']:.4f}"] for r in run]),'',
        '## Phases','',table(['Cohort','Generated/step','Share','Output/answer','Seconds/step','Allocated $/step','List $/step'],[
        [k,f"{v['generated_per_step']:.1f}",f"{v['share']:.1%}",f"{v['output_mean']:.1f}",f"{v['seconds']:.1f}",f"{v['cost']:.4f}",f"{v['list_cost']:.4f}"] for k,v in phases.items()])]
    (OUT/'reconstructed-tables.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    result=dict(summaries=summaries,phases=phases,decomposition=decomposition,pooled_token_overhead_factor=eta,list_model_errors=errs,fixed_smoke_lengths_run_prediction=predicted_fixed)
    (OUT/'reconstruction.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
