"""Final artifact-preservation and report consistency checks."""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'audit/scratch'

def main():
    m=json.loads((OUT/'run1-mechanical.json').read_text())
    x=json.loads((OUT/'run1-extended.json').read_text())
    protected=dict(m['hashes'],**x['source_module_sha256'])
    unchanged={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in protected.items()}
    report=ROOT/'audit/run1-result-integrity.md'
    text=report.read_text(encoding='utf-8')
    targets=re.findall(r'\]\(([^)]+)\)',text)
    missing=[p for p in targets if not (report.parent/p).exists()]
    result=dict(protected_hashes_unchanged=unchanged,missing_report_links=missing,
        em_dash_in_report=chr(0x2014) in text,
        em_dash_in_audit_scripts=[p.name for p in OUT.glob('run1_*.py') if chr(0x2014) in p.read_text(encoding='utf-8')],
        discordant_rows_in_report=len(re.findall(r'^\| L[1-4] \| test-\d{4} \|',text,re.M)),
        expected_discordant_rows=len(m['discordant']),
        repository_mismatches=json.loads((OUT/'run1-rescore-repo.json').read_text())['mismatches'],
        wheel_mismatches=json.loads((OUT/'run1-rescore-wheel.json').read_text())['mismatches'])
    assert all(unchanged.values())
    assert not missing and not result['em_dash_in_report'] and not result['em_dash_in_audit_scripts']
    assert result['discordant_rows_in_report']==result['expected_discordant_rows']==70
    assert result['repository_mismatches']==result['wheel_mismatches']==[]
    (OUT/'run1-final-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
