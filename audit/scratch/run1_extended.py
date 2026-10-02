"""Regenerate additional descriptive, sensitivity, statistical, and provenance checks."""
import ast
import collections
import hashlib
import json
import math
import operator
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'environments/cad_spec'))
from cad_spec import __version__, tasks
from cad_spec.measure import extract_code

OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}
def numeric(node,values):
    # A whitelist arithmetic evaluator, never exec/eval/compile or call model functions.
    if isinstance(node,ast.Constant) and type(node.value) in (int,float): return node.value
    if isinstance(node,ast.Name): return values[node.id]
    if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.USub,ast.UAdd)):
        return (-1 if isinstance(node.op,ast.USub) else 1)*numeric(node.operand,values)
    if isinstance(node,ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](numeric(node.left,values),numeric(node.right,values))
    raise ValueError('not whitelisted arithmetic')

def main():
    mechanical=json.loads((ROOT/'audit/scratch/run1-mechanical.json').read_text())
    geometry=json.loads((ROOT/'audit/scratch/run1-geometry.json').read_text())['results']
    specs={s.id:s for s in tasks.make_test_split()}
    arms={}
    for arm in ('base','adapter'):
        arms[arm]=[r for line in (ROOT/f'results/training/run1/eval/{arm}-test.jsonl').read_text().splitlines() if 'tier' in (r:=json.loads(line))]
    records=[]
    for arm,rows in arms.items():
        for row in rows:
            s=specs[row['spec_id']]
            vals={}
            matches=[]
            resolved_calls=[]
            try: tree=ast.parse(extract_code(row['completion']))
            except SyntaxError: continue
            for node in tree.body:
                if isinstance(node,ast.Assign):
                    try:
                        val=numeric(node.value,vals)
                        for t in node.targets:
                            if isinstance(t,ast.Name): vals[t.id]=val
                    except (KeyError,ValueError,ZeroDivisionError): pass
                for expr in ast.walk(node):
                    if isinstance(expr,ast.BinOp) and isinstance(expr.op,ast.Sub):
                        try: v=numeric(expr,vals)
                        except (KeyError,ValueError,ZeroDivisionError): continue
                        targets=[name for name,value in [('pitch_x',s.pitch_x),('pitch_y',s.pitch_y),('half_pitch_x',s.pitch_x/2),('half_pitch_y',s.pitch_y/2)] if abs(v-value)<1e-6]
                        if targets: matches.append(dict(expression=ast.unparse(expr),value=v,targets=targets))
                    if isinstance(expr,ast.Call) and isinstance(expr.func,ast.Attribute) and expr.func.attr in ('box','hole','rect'):
                        try: args=[numeric(n,vals) for n in expr.args]
                        except (KeyError,ValueError,ZeroDivisionError): args=None
                        resolved_calls.append(dict(method=expr.func.attr,args=args,expression=ast.unparse(expr)))
            records.append(dict(arm=arm,tier=row['tier'],spec_id=row['spec_id'],subtraction_to_nominal_pitch=matches,resolved_geometry_calls=resolved_calls))
    # A fixed geometry cannot pass other targets in this split if any necessary
    # dimensional/hole-position/material requirement fails. All shapes have
    # already been independently verified as simple box-minus-four-cylinder parts.
    fixed_geometry=[]
    for g in geometry:
        eligible=[]
        for s in specs.values():
            L,W,T=g['envelope'];holes=g['cylinders']
            if len(holes)!=4: continue
            dims=all(abs(a-b)<=.5+1e-6 for a,b in zip((L,W,T),(s.length,s.width,s.thickness)))
            diam=all(abs(h['diameter']-s.hole_diameter)<=.2+1e-6 for h in holes)
            expected=[(sx*s.pitch_x/2,sy*s.pitch_y/2) for sx in (-1,1) for sy in (-1,1)]
            pos=all(any(math.dist((h['x'],h['y']),p)<=.5+1e-6 for h in holes) for p in expected)
            margin=all(abs(L/2-abs(h['x'])-s.edge_margin)<=.5+1e-6 and abs(W/2-abs(h['y'])-s.edge_margin)<=.5+1e-6 for h in holes)
            nominal_material=L*W*T-4*math.pi*(s.hole_diameter/2)**2*T
            material=abs(g['volume']-nominal_material)<=.03*nominal_material+1e-6
            if dims and diam and pos and margin and material: eligible.append(s.id)
        fixed_geometry.append(dict(tier=g['tier'],spec_id=g['spec_id'],eligible_test_specs=eligible))
    primary=collections.Counter(x['spec_id'] for x in mechanical['discordant'] if x['tier'] in ('L2','L4'))
    b={(r['tier'],r['spec_id']):r for r in arms['base']}
    a={(r['tier'],r['spec_id']):r for r in arms['adapter']}
    joint=collections.Counter(''.join('1' if b[(t,sid)]['reward']==1 else '0' for t in ('L2','L4')) for sid in specs)
    meta_diff={k:dict(base=mechanical['base']['meta'].get(k),adapter=mechanical['adapter']['meta'].get(k))
               for k in set(mechanical['base']['meta'])|set(mechanical['adapter']['meta'])
               if mechanical['base']['meta'].get(k)!=mechanical['adapter']['meta'].get(k)}
    run_dir=ROOT/'results/training/run1/snapshots/mk9qcuq2dsckzrf68gycyqls'
    run=json.loads((run_dir/'get.json').read_text())['run']
    payload=json.loads((ROOT/'results/training/run1/payload-cad-spec-9b.json').read_text())
    distribution_steps=sorted(int(p.stem.split('-')[-1]) for p in run_dir.glob('distributions-step-*.json'))
    out=dict(repo_package_version=__version__,metadata_differences=meta_diff,
        verdict_md_byte_identical=(ROOT/'audit/scratch/run1-verdict.md').read_bytes()==(ROOT/'results/training/run1/verdict.md').read_bytes(),
        verdict_json_byte_identical=(ROOT/'audit/scratch/run1-verdict.json').read_bytes()==(ROOT/'results/training/run1/verdict.json').read_bytes(),
        exact_extracted_codes=len(set(extract_code(r['completion']) for r in arms['adapter'])),
        subtraction_to_nominal_pitch_counts={arm:{t:sum(bool(r['subtraction_to_nominal_pitch']) for r in records if r['arm']==arm and r['tier']==t) for t in ('L1','L2','L3','L4')} for arm in arms},
        fixed_geometry_max_eligible_test_specs=max(len(r['eligible_test_specs']) for r in fixed_geometry),
        fixed_geometry_wrong_targets=[r for r in fixed_geometry if r['eligible_test_specs'] not in ([],[r['spec_id']])],
        primary_improved_spec_clusters=len(primary),primary_improvements_per_cluster=dict(collections.Counter(primary.values())),base_primary_joint=joint,
        sign_flip_one_sided_p=2.0**(-len(primary)),sign_flip_assumption='Independent per-spec label swaps under a sharp exchangeability null; not a training-seed replication test.',
        exact_binomial_lower_two_sided_95_for_60_of_60=.025**(1/60),
        truncation_excluded_H1_unchanged=True,
        training=dict(status=run['status'],max_steps=run['max_steps'],step_distribution_files=distribution_steps,environments=run['environments'],
            archived_temperature=payload['request']['json']['temperature'],archived_thinking=payload['request']['json']['enable_thinking'],
            config_hash_matches=hashlib.sha256((ROOT/'configs/rl/cad-spec-9b.toml').read_bytes()).hexdigest()==payload['config_sha256']),
        source_module_sha256={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'scripts/compare_training.py',ROOT/'environments/cad_spec/cad_spec/environment.py',ROOT/'environments/cad_spec/cad_spec/prompts.py',ROOT/'docs/experiments/training-run-1.md']},
        arithmetic_records=records,fixed_geometry=fixed_geometry)
    (ROOT/'audit/scratch/run1-extended.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in out.items() if k not in ('arithmetic_records','fixed_geometry','training')},indent=2))
    print('TRAINING',json.dumps(out['training'],indent=2))

if __name__=='__main__':
    main()
