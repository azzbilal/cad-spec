"""PROPOSAL ONLY. Not connected to a run in this audit.

Future invocation needs --execute; otherwise it is an offline decision preview.
The limit is on RECORDED spend. A reserve must cover unreported work and teardown.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
from decimal import Decimal

TERMINAL = {'STOPPED', 'COMPLETED', 'FAILED', 'CANCELLED', 'CANCELED'}

def command(args, timeout=20):
    env = dict(os.environ)
    env.pop('SSLKEYLOGFILE', None)
    env.update(PYTHONIOENCODING='utf-8', PYTHONUTF8='1',
               PRIME_DISABLE_VERSION_CHECK='1', NO_COLOR='1', TERM='dumb')
    # argv, not shell interpolation; decoding cannot crash on Windows glyphs.
    result = subprocess.run(['prime', *args], env=env, capture_output=True,
                            text=True, encoding='utf-8', errors='replace',
                            timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError('prime failed: '+str(result.returncode))
    return result.stdout

def validate_usage(data, run_id, previous):
    if data.get('run_id') != run_id:
        raise ValueError('wrong run id')
    cost = Decimal(str(data['total_cost_usd']))
    if not cost.is_finite() or cost < 0 or cost < previous:
        raise ValueError('invalid or regressing spend')
    status = data.get('status')
    if not isinstance(status, str) or not status:
        raise ValueError('missing status')
    # The endpoint has no billing freshness timestamp. An unchanged total alone
    # cannot prove it is current; max-runtime is an independent stop condition.
    return cost, status.upper()

def stop_and_verify(run_id, call=command, sleep=time.sleep):
    # Stop return code 0 need not mean terminal. Always verify get.status.
    for _ in range(3):
        try:
            call(['train', 'stop', run_id, '--force'], timeout=35)
        except Exception:
            pass  # stop could have reached the server before the client timed out
        try:
            data = json.loads(call(['train', 'get', run_id, '-o', 'json']))
            if data['run']['id'] == run_id and data['run']['status'].upper() in TERMINAL:
                return
        except Exception:
            pass
        sleep(5)
    raise RuntimeError('STOP UNCONFIRMED. Manual intervention required for '+run_id)

def monitor(run_id, limit, reserve, max_seconds, poll=15, call=command,
            sleep=time.sleep, now=time.monotonic, emit=print):
    trigger = limit - reserve
    if trigger <= 0 or reserve < 0 or max_seconds <= 0 or not 1 <= poll <= 30:
        raise ValueError('invalid guard policy')
    start = now()
    previous = Decimal('0')
    while True:
        try:
            # Spend and identity come from usage, never the text log or a step.
            cost, status = validate_usage(json.loads(call(
                ['train', 'usage', run_id, '-o', 'json'])), run_id, previous)
            previous = cost
            emit(json.dumps({'run_id': run_id, 'recorded_usd': str(cost),
                             'trigger_usd': str(trigger), 'status': status}))
            if status in TERMINAL:
                return
            reason = ('recorded spend limit' if cost >= trigger else
                      'runtime limit' if now() - start >= max_seconds else None)
        except Exception:
            # Any unreadable usage, timeout, rate-limit, or wrong identity stops
            # the run. Availability is traded for budget protection.
            reason = 'usage unavailable or invalid'
        if reason:
            emit(reason)
            stop_and_verify(run_id, call, sleep)
            return
        sleep(poll)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('run_id')
    ap.add_argument('--limit', type=Decimal, required=True)
    ap.add_argument('--reserve', type=Decimal, required=True)
    ap.add_argument('--max-seconds', type=int, required=True)
    ap.add_argument('--poll', type=int, default=15)
    ap.add_argument('--execute', action='store_true')
    args = ap.parse_args()
    if not args.limit.is_finite() or not args.reserve.is_finite():
        ap.error('amounts must be finite')
    if not args.execute:
        print(json.dumps({'preview_only': True, 'run_id': args.run_id,
                          'stop_at_recorded_usd': str(args.limit-args.reserve)}))
        return
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    monitor(args.run_id, args.limit, args.reserve, args.max_seconds, args.poll)

if __name__ == '__main__':
    main()
