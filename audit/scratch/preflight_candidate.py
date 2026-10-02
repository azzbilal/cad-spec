"""Offline forecast. No provider calls. All inputs must be registered.

No forecast substitutes for a provider-enforced dollar or dispatch bound.
"""
import argparse
import math

def forecast(steps, batch, group, flat, input_tokens, output_tokens,
             trained_tokens, overhead=1.54, margin=1.25,
             input_price=.2, output_price=.6, training_price=.6):
    if not 0 <= flat < 1 or batch <= 0 or group < 2 or batch % group:
        raise ValueError('invalid grouping or flat fraction')
    groups=(batch/group)/(1-flat)
    inference=groups*group*(input_price*input_tokens+output_price*output_tokens)/1e6
    training=batch*trained_tokens*training_price/1e6
    return steps*(training+overhead*inference)*margin

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['steps','batch','group']:
        ap.add_argument('--'+name,type=int,required=True)
    for name in ['flat','input-tokens','output-tokens','trained-tokens','wallet',
                 'ceiling','prior-spend','reserve','evaluation-reserve']:
        ap.add_argument('--'+name,type=float,required=True)
    ap.add_argument('--enforced-cap-verified',action='store_true')
    a=ap.parse_args()
    if any(not math.isfinite(v) or v < 0 for v in vars(a).values() if isinstance(v,(int,float))):
        ap.error('inputs must be finite and nonnegative')
    predicted=forecast(a.steps,a.batch,a.group,a.flat,a.input_tokens,
                       a.output_tokens,a.trained_tokens)
    available=min(a.wallet-a.evaluation_reserve,a.ceiling-a.prior_spend)-a.reserve
    print(f'forecast_with_margin=${predicted:.4f}; available=${available:.4f}')
    if not a.enforced_cap_verified or predicted > available:
        raise SystemExit('REFUSE LAUNCH: missing verified enforcement or insufficient budget')
    print('PASS budget preflight; this command never launches a run')

if __name__=='__main__':main()
