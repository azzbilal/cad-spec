import ast,json,re
from pathlib import Path
p=Path('audit')
text=(p/'run1-cost-report.md').read_text(encoding='utf-8')
assert '\u2014' not in text
links=re.findall(r'\]\(([^)]+)\)',text)
missing=[]
for link in links:
 if link.startswith('http'):continue
 target=re.sub(r':\d+$','',link)
 if not (p/target).exists():missing.append(link)
assert not missing,missing
for name in ['reconstruct_cost.py','extra_analysis.py','spend_guard_candidate.py','preflight_candidate.py','test_guard_offline.py']:
 ast.parse((p/'scratch'/name).read_text(encoding='utf-8'))
base=Path('results/training/run1')
a=json.loads((base/'payload-cad-spec-9b-smoke.json').read_text(encoding='utf-8'))['request']['json']
b=json.loads((base/'payload-cad-spec-9b.json').read_text(encoding='utf-8'))['request']['json']
diff=[k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)]
assert sorted(diff)==['max_steps','name'],diff
summary=json.loads((p/'reconstruction.json').read_text(encoding='utf-8'))
assert len(list((p/'run-steps.csv').open(encoding='utf-8')))==39
assert 38*128==summary['summaries']['run']['sums']['trained']
print('PASS: report links, Python syntax, both payloads, 38-step table, no em dashes')
