"""All calls injected. No Prime CLI process can be started by these tests."""
import json
from decimal import Decimal
from unittest.mock import patch
import spend_guard_candidate as guard

def exercise(costs, expected_stop, stop_fail=False, terminal=False):
    calls=[]
    values=iter(costs)
    def fake(args, **kwargs):
        calls.append(args)
        if args[1]=='usage':
            value=next(values)
            if isinstance(value,Exception): raise value
            if isinstance(value,str): return value
            return json.dumps(dict(run_id='fixture', total_cost_usd=value,
                                   status='STOPPED' if terminal else 'RUNNING'))
        if args[1]=='stop':
            if stop_fail: raise TimeoutError('transport timed out')
            return 'stop requested'
        if args[1]=='get':
            return json.dumps({'run': {'id':'fixture','status':'STOPPED'}})
        raise AssertionError(args)
    # Wall-clock expiry is exercised separately; no actual sleeping here.
    guard.monitor('fixture',Decimal('10'),Decimal('1'),300,
                  call=fake,sleep=lambda _:None,now=lambda:0,emit=lambda _:None)
    assert any(a[1]=='stop' for a in calls)==expected_stop
    assert all(a[0]=='train' and a[1] in {'usage','stop','get'} for a in calls)

with patch.object(guard.subprocess,'run',side_effect=AssertionError('real process forbidden')):
    exercise([1,5,9],True)
    exercise([9],True,stop_fail=True)
    exercise([TimeoutError()],True)
    exercise(['Error: HTTP 429'],True)
    exercise(['{"run_id":"wrong"}'],True)
    exercise([5,4],True)
    exercise([1],False,terminal=True)
    calls=[]
    def fake(args,**kwargs):
        calls.append(args)
        return json.dumps({'run_id':'fixture','total_cost_usd':0,'status':'RUNNING'}) if args[1]=='usage' else json.dumps({'run':{'id':'fixture','status':'STOPPED'}})
    ticks=iter([0,400])
    guard.monitor('fixture',Decimal('10'),Decimal('1'),300,call=fake,
                  sleep=lambda _:None,now=lambda:next(ticks),emit=lambda _:None)
    assert any(a[1]=='stop' for a in calls)
# Encoding and env construction tested with a mocked child only.
class Result:
    returncode=0
    stdout='\u2713'
with patch.dict(guard.os.environ,{'SSLKEYLOGFILE':'fixture-sensitive-path'}):
    with patch.object(guard.subprocess,'run',return_value=Result()) as mock:
        assert guard.command(['train','usage','fixture','-o','json'])=='\u2713'
        kwargs=mock.call_args.kwargs
        assert 'SSLKEYLOGFILE' not in kwargs['env']
        assert kwargs['encoding']=='utf-8' and kwargs['errors']=='replace'
        assert kwargs['env']['PYTHONIOENCODING']=='utf-8'
print('PASS: 9 offline guard scenarios; all CLI calls mocked')
