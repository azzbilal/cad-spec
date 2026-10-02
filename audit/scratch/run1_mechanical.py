"""Offline integrity, leakage, hygiene, and paired descriptive audit."""
import ast
import collections
import copy
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'environments/cad_spec'))
from cad_spec import tasks, prompts
from cad_spec.measure import extract_code

OUT = ROOT / 'audit/scratch'
TIERS = ('L1', 'L2', 'L3', 'L4')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(label):
    path = ROOT / f'results/training/run1/eval/{label}-test.jsonl'
    recs = [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
    return recs[0]['meta'], [x for x in recs if 'tier' in x], recs[-1]['end']

class Normalize(ast.NodeTransformer):
    def __init__(self, rename=False):
        self.names = {}
        self.rename = rename
    def visit_Constant(self, node):
        if type(node.value) in (int, float):
            return ast.copy_location(ast.Constant(value=0), node)
        return node
    def visit_Name(self, node):
        if self.rename and node.id not in ('cq', 'cadquery', 'result', 'True', 'False', 'range', 'math'):
            node.id = self.names.setdefault(node.id, 'v' + str(len(self.names)))
        return node

def features(row):
    code = extract_code(row['completion'])
    out = {'tier': row['tier'], 'spec_id': row['spec_id'], 'code_chars': len(code),
           'lines': len(code.splitlines()), 'comments': sum(x.lstrip().startswith('#') for x in code.splitlines())}
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return dict(out, syntax_error=str(exc))
    nodes = list(ast.walk(tree))
    imports = []
    for node in nodes:
        if isinstance(node, ast.Import): imports.extend(x.name for x in node.names)
        if isinstance(node, ast.ImportFrom): imports.append(node.module)
    attrs = [x.attr for x in nodes if isinstance(x, ast.Attribute)]
    names = [x.id for x in nodes if isinstance(x, ast.Name)]
    calls = [ast.unparse(x.func) for x in nodes if isinstance(x, ast.Call)]
    stores = [ast.unparse(t) for x in nodes if isinstance(x, (ast.Assign, ast.AnnAssign, ast.AugAssign))
              for t in (x.targets if isinstance(x, ast.Assign) else [x.target]) if isinstance(t, (ast.Attribute, ast.Subscript))]
    assignments = [x for x in tree.body if isinstance(x, ast.Assign)]
    arithmetic = [ast.unparse(x) for x in assignments if any(isinstance(n, ast.BinOp) for n in ast.walk(x.value))]
    out.update(imports=imports, calls=calls, attribute_or_subscript_writes=stores,
               dangerous_names=sorted(set(names) & {'os','sys','subprocess','importlib','eval','exec','open','getattr','setattr','globals','locals','vars','__import__','compile','requests','socket','urllib'}),
               introspection_attrs=sorted(x for x in set(attrs) if x.startswith('__')),
               try_count=sum(isinstance(x, ast.Try) for x in nodes),
               function_count=sum(isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)) for x in nodes),
               assigned_names=[ast.unparse(t) for x in assignments for t in x.targets],
               arithmetic_assignments=arithmetic,
               geometry_calls=[ast.unparse(x) for x in nodes if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr in ('box','rect','hole','pushPoints','rarray','translate','cut','extrude')],
               numeric_constants=[x.value for x in nodes if isinstance(x, ast.Constant) and type(x.value) in (int,float)],
               ast_structure=ast.dump(Normalize().visit(copy.deepcopy(tree)), include_attributes=False),
               renamed_structure=ast.dump(Normalize(True).visit(copy.deepcopy(tree)), include_attributes=False))
    return out

def main():
    out = {}
    paths = [ROOT / f'results/training/run1/eval/{x}-test.jsonl' for x in ('base','adapter')]
    paths += [ROOT / f'results/training/run1/verdict.{x}' for x in ('md','json')]
    out['hashes'] = {str(p.relative_to(ROOT)).replace('\\','/'): sha(p) for p in paths}
    test = tasks.make_test_split()
    smap = {s.id:s for s in test}
    out['test_fingerprint'] = tasks.split_fingerprint(test)
    out['system_prompt_sha256'] = prompts.fingerprint(prompts.system_prompt(True))
    arms = {}
    allfeatures = {}
    for label in ('base', 'adapter'):
        meta, rows, end = load(label)
        arms[label] = rows
        f = [features(r) for r in rows]
        allfeatures[label] = f
        expected = {(t,s.id) for t in TIERS for s in test}
        out[label] = dict(meta=meta, end=end, rows=len(rows),
            keys_equal_expected=set((r['tier'],r['spec_id']) for r in rows)==expected,
            duplicate_keys=len(rows)-len(set((r['tier'],r['spec_id']) for r in rows)),
            prompt_mismatches=[(r['tier'],r['spec_id']) for r in rows if r['prompt']!=tasks.prompt_for(smap[r['spec_id']],r['tier'],'test')],
            local_system_prompt_equal=meta['system_prompt']==prompts.system_prompt(True),
            served_models=dict(collections.Counter(r.get('served_model') for r in rows)),
            row_seeds=dict(collections.Counter(r.get('seed') for r in rows)),
            finish_reasons=dict(collections.Counter(r.get('finish_reason') for r in rows)),
            flags={key:sum(bool(r.get(key)) for r in rows) for key in ('api_error','error','truncated','timeout','degenerate','retries','attempts')},
            truncated_rows=[{'tier':r['tier'],'spec_id':r['spec_id'],'reward':r['reward']} for r in rows if r.get('truncated')],
            totals={key:sum(r['usage'].get(key,0) or 0 for r in rows) for key in ('prompt_tokens','completion_tokens')},
            computed_cost=sum(r['cost_usd'] for r in rows),
            usage_reported_cost=sum(r['usage'].get('cost',0) or 0 for r in rows),
            lengths={t:{key: {'mean':statistics.mean(vals), 'median':statistics.median(vals), 'min':min(vals), 'max':max(vals)}
                for key,vals in [('chars',[len(r['completion']) for r in rows if r['tier']==t]),
                                 ('tokens',[r['usage']['completion_tokens'] for r in rows if r['tier']==t])]} for t in TIERS},
            structures={t:{'exact_answers':len(set(r['completion'] for r in rows if r['tier']==t)),
                'numeric_normalized':len(set(x.get('ast_structure','invalid') for x in f if x['tier']==t)),
                'renamed_normalized':len(set(x.get('renamed_structure','invalid') for x in f if x['tier']==t)),
                'arithmetic_assignments':sum(bool(x.get('arithmetic_assignments')) for x in f if x['tier']==t),
                'variables':sum(bool(x.get('assigned_names')) and len(x['assigned_names'])>1 for x in f if x['tier']==t),
                'comments':sum(x['comments']>0 for x in f if x['tier']==t)} for t in TIERS})
    out['prompt_arms_equal'] = all(b['prompt']==a['prompt'] for b,a in zip(arms['base'],arms['adapter']))
    train, dev = tasks.make_splits()
    params = tasks._params
    from cad_spec.environment import _build_dataset, _build_eval_dataset
    dataset = _build_dataset(TIERS)
    evaldata = _build_eval_dataset(TIERS)
    l3_train = [tasks.prompt_for(s,'L3','train') for s in train]
    # Also check the embedded rev A geometry, not just target specs.
    train_sources = [tasks.edit_source(s) for s in train]
    dev_sources = [tasks.edit_source(s) for s in dev]
    out['leakage'] = dict(train_size=len(train), eval_size=len(dev), test_size=len(test),
        train_id_overlap=sorted(set(s.id for s in train)&set(s.id for s in test)),
        eval_id_overlap=sorted(set(s.id for s in dev)&set(s.id for s in test)),
        train_tuple_overlap=[s.id for s in test if params(s) in set(map(params,train))],
        eval_tuple_overlap=[s.id for s in test if params(s) in set(map(params,dev))],
        embedded_train_revA_tuple_overlap=[s.id for s in test if params(s) in set(map(params,train_sources))],
        embedded_eval_revA_tuple_overlap=[s.id for s in test if params(s) in set(map(params,dev_sources))],
        exact_L3_prompt_overlap=[s.id for s in test if tasks.prompt_for(s,'L3','test') in l3_train],
        train_wording_indices=sorted(set(tasks._stable_pick(s.id,tasks._PROSE_TRAIN) for s in train)),
        test_wording_indices=sorted(set(tasks._stable_pick(s.id,tasks._PROSE_EVAL) for s in test)),
        environment_train_rows=len(dataset), environment_eval_rows=len(evaldata),
        dataset_test_id_overlap=sorted(set(dataset['answer']) & set(smap)),
        dataset_prompt_mismatches=[i for i,r in enumerate(dataset) if r['question']!=tasks.prompt_for(next(s for s in train if s.id==r['answer']),r['info']['tier'],'train')],
        train_system_prompt=out['system_prompt_sha256'])
    af = allfeatures['adapter']
    out['hygiene'] = dict(import_counts=dict(collections.Counter(n for x in af for n in x.get('imports',[]))),
        syntax_errors=[x for x in af if 'syntax_error' in x],
        dangerous=[{k:x[k] for k in ('tier','spec_id','dangerous_names','introspection_attrs','attribute_or_subscript_writes','try_count','function_count')} for x in af
                   if x.get('dangerous_names') or x.get('introspection_attrs') or x.get('attribute_or_subscript_writes') or x.get('try_count') or x.get('function_count')],
        max_code_chars=max(x['code_chars'] for x in af), max_lines=max(x['lines'] for x in af),
        exact_answers=len(set(r['completion'] for r in arms['adapter'])),
        numeric_normalized=len(set(x['ast_structure'] for x in af)),
        renamed_normalized=len(set(x['renamed_structure'] for x in af)),
        call_counts=dict(collections.Counter(n for x in af for n in x.get('calls',[]))))
    bm = {(r['tier'],r['spec_id']):r for r in arms['base']}
    discordant = []
    failures = []
    for a in arms['adapter']:
        b = bm[(a['tier'],a['spec_id'])]
        if a['reward'] != 1:
            failures.append(dict(tier=a['tier'],spec_id=a['spec_id'],reward=a['reward'],failed=[k for k,v in a['checks'].items() if not v],completion=a['completion']))
        if (b['reward']==1)!=(a['reward']==1):
            discordant.append(dict(tier=a['tier'],spec_id=a['spec_id'],base_pass=b['reward']==1,adapter_pass=a['reward']==1,
                base_failed=[k for k,v in b['checks'].items() if not v], adapter_failed=[k for k,v in a['checks'].items() if not v],base_error=b['error'],adapter_error=a['error']))
    out['discordant'] = discordant
    out['adapter_failures'] = failures
    out['L4_failure_checks'] = dict(collections.Counter(k for x in discordant if x['tier']=='L4' for k in x['base_failed']))
    (OUT/'run1-mechanical.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    (OUT/'run1-code-features.json').write_text(json.dumps(allfeatures,indent=2),encoding='utf-8')
    print(json.dumps({k:out[k] for k in ('hashes','test_fingerprint','leakage','hygiene','L4_failure_checks')},indent=2))
    for label in ('base','adapter'):
        print(label, json.dumps({k:v for k,v in out[label].items() if k not in ('meta','end')},indent=2))
    print('Adapter failures',json.dumps(failures,indent=2))
    print('Discordant count',len(discordant))

if __name__=='__main__':
    main()
