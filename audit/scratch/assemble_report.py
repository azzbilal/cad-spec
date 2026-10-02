from pathlib import Path
p=Path('audit')
parts=[(p/name).read_text(encoding='utf-8') for name in ['run1-cost-report-prefix.md','reconstructed-tables.md','run1-cost-report-suffix.md']]
text='\n'.join(parts)
assert '\u2014' not in text
(p/'run1-cost-report.md').write_text(text,encoding='utf-8')
print('Report written:',len(text.splitlines()),'lines;',len(text),'characters')
