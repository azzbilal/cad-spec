import hashlib, json, urllib.request
from pathlib import Path
from datetime import datetime, timezone
out=Path('audit/sources'); out.mkdir(exist_ok=True)
urls={
 'advanced-configs.md':'https://docs.primeintellect.ai/hosted-training/advanced-configs.md',
 'models-and-pricing.md':'https://docs.primeintellect.ai/hosted-training/models-and-pricing.md',
 'full-finetuning.md':'https://docs.primeintellect.ai/hosted-training/full-finetuning.md',
 'update-user-limits.md':'https://docs.primeintellect.ai/api-reference/admin-users/update-user-limits.md',
 'update-user-wallet-settings.md':'https://docs.primeintellect.ai/api-reference/admin-users/update-user-wallet-settings.md',
 'prime-rl-commit.json':'https://api.github.com/repos/PrimeIntellect-ai/prime-rl/commits/main',
}
records=[]
def fetch(name,url):
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'cad-spec-cost-audit'})
  data=urllib.request.urlopen(req,timeout=30).read(); (out/name).write_bytes(data)
  records.append(dict(file=name,url=url,sha256=hashlib.sha256(data).hexdigest(),captured_at_utc=datetime.now(timezone.utc).isoformat()))
  print(name,len(data))
  return data
 except Exception as e: print(name,type(e).__name__,str(e))
for name,url in urls.items(): fetch(name,url)
commit=json.loads((out/'prime-rl-commit.json').read_text(encoding='utf-8'))['sha']
print('prime-rl reference commit',commit)
for name,path in {
 'upstream-orchestrator-config.py':'packages/prime-rl-configs/src/prime_rl/configs/orchestrator.py',
 'upstream-orchestrator.py':'src/prime_rl/orchestrator/orchestrator.py',
 'upstream-train-sink.py':'src/prime_rl/orchestrator/train_sink.py',
 'upstream-concurrency.py':'src/prime_rl/orchestrator/concurrency.py',
}.items(): fetch(name,'https://raw.githubusercontent.com/PrimeIntellect-ai/prime-rl/'+commit+'/'+path)
for name,path in {
 'registered-orchestrator-config.py':'packages/prime-rl-configs/src/prime_rl/configs/orchestrator.py',
 'registered-train-sink.py':'src/prime_rl/orchestrator/train_sink.py',
 'registered-orchestrator.py':'src/prime_rl/orchestrator/orchestrator.py',
 'registered-legacy.py':'packages/prime-rl-configs/src/prime_rl/configs/legacy.py',
 'registered-grpo.py':'src/prime_rl/orchestrator/algo/grpo.py',
}.items(): fetch(name,'https://raw.githubusercontent.com/PrimeIntellect-ai/prime-rl/9eacd47/'+path)
cli=Path.home()/'AppData/Roaming/uv/tools/prime/Lib/site-packages/prime_cli'
for name,path in {'installed-cli-rl.py':'commands/rl.py','installed-api-rl.py':'api/rl.py','installed-cli-usage.py':'commands/usage.py','installed-api-billing.py':'api/billing.py'}.items():
 data=(cli/path).read_bytes(); (out/name).write_bytes(data)
 records.append(dict(file=name,local_source=str(cli/path),sha256=hashlib.sha256(data).hexdigest()))
(out/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
