# Training run 1: smoke-test acceptance (step 5)

Run `k3rwpbbk5sio4936onuai7ok` (`configs/rl/cad-spec-9b-smoke.toml`), Prime
Hosted Training, Prime CLI 0.8.0. Created 2026-09-30 14:49:49, started
14:50:13, completed 14:56:10 (about 6 minutes, setup included). Status
COMPLETED, no error message, no failure analysis. Source of every figure:
`prime train get -o json`, `logs`, `metrics`, `distributions`, `usage` for
this run, captured as dated, hashed snapshots by `scripts/capture_run.py` in
`results/training/run1/snapshots/k3rwpbbk5sio4936onuai7ok/` (`manifest.json`
lists each command, UTC time, CLI version and SHA-256).

## Registered acceptance checks (pre-registration section 6.1)

| # | Check | Evidence | Verdict |
|---|---|---|---|
| 1 | The three environments load at the registered version | Run record: `cad-spec-L4`, `cad-spec-L2`, `cad-spec-L1-L3`, all `bazzouzi/cad-spec` version `0.4.5` (version id `s41pd72x99yh706fv3vnftl8`), args `reward = "binary"`, `hints = true`, tiers as registered, ratios 0.5 / 0.25 / 0.25; pre-batch filter `zero_advantage` enforced. Logs: environments ready with 200, 200 and 400 train tasks | pass |
| 2 | Temperature 0.7 | **Sent, not independently confirmed as applied.** The Prime CLI passes `cfg.sampling.temperature` to `create_run` (`prime_cli/commands/rl.py:1827`) and writes `payload["temperature"]` (`prime_cli/api/rl.py:299-300`); displayed as 0.7 before launch; the exact request for this config, recorded without sending by `scripts/archive_run_payload.py`, is `results/training/run1/payload-cad-spec-9b-smoke.json` (`temperature: 0.7`, `enable_thinking: false`). The service echoes neither setting in the run record, logs or rollout records, so that it applied them rests on the payload, not on a service-side record | pass, as sent |
| 3 | Rewards of both 0 and 1 at every step | Trained-batch reward counts (0 / 1): step 1: 59 / 69; step 2: 70 / 58; step 3: 56 / 72; step 4: 54 / 74; step 5: 51 / 77. No trained sample with zero advantage at step 5 | pass |
| 4 | No scoring errors | `has_error` 0.0 in all three environments; "Error 0.0%" at every logged step; scoring time mean 0.07 s per answer (one 10 s first-call warm-up) | pass |
| 5 | Cost per step | Recorded charges (`prime train usage -o json`): training **$0.3539**, inference **$0.3065** (input and output combined), total **$0.6604** for 5 steps: **$0.13208 per step**. Tokens: training 589.78K, inference input 892.29K, output 402.80K. At list prices the inference tokens would cost $0.4202 ($0.1785 + $0.2417); the table view of `prime train usage` shows such rounded per-bucket amounts ($0.18, $0.24), which do not add up to the recorded total. The recorded charge is lower than list price for reasons the usage record does not state; the budget rule uses the recorded charges. Training tokens / 5 = 118K per step = 128 trained answers x 925 tokens (measured mean) | pass |

## Other observations (not registered checks)

- Steps 3 to 5 in the log: 25 s, 81 s, 45 s; truncation 0.0 to 2.5%.
- Trained fraction after the zero-advantage filter: 64%, 64%, 76% of
  generated answers; at step 5, half of the L4 groups were flat (zero
  advantage), none of the L2 or L1-L3 groups.
- Realized mix of trained groups: L4 48 to 56%, L2 24%, L1-L3 20 to 29%
  (registered 50 / 25 / 25).
- Platform filters: our pre-batch zero-advantage filter, plus the service's
  post-batch gibberish and repetition filters in monitoring mode only and a
  second zero-advantage filter (enforced).
- Hyperparameters the run record leaves unset (service defaults):
  `learning_rate`, `lora_alpha`, `oversampling_factor`, `max_async_level`.
- Rewards during these 5 steps are not interpreted: the registration judges
  the run only on the locked test split.

## Budget rule (pre-registration section 6.2)

Smoke tests so far, recorded charges: $0.0000 (`b32pcagfy8t4bqf2lnc6dep7`),
$0.0000 (`jvryf7tsn20jw66cfxesbp08`), $0.0250 (`jkqd5k12g1g5kvqyhmfg012k`),
$0.6604 (`k3rwpbbk5sio4936onuai7ok`): **$0.6854**.

`max_steps = floor((15.00 - 0.6854 - 0.50) / 0.13208) = floor(104.59) = 104`
(at most 150; at least 30). Projected training cost 104 x $0.13208 = $13.74;
total with the smoke tests $14.42, **$0.58 under the $15 ceiling**.

**Sensitivity.** That headroom is 4.2% of the projected training cost: a
rise of about 4.2% in the average cost per step would use all of it. Longer
answers, a larger share of flat groups (more generation per trained batch),
or a different billing basis would each raise it. Monitoring: the run's own
recorded spend must stay under **$14.31** (15.00 - 0.6854); at about $0.132
per step it should end near $13.74. Per section 6.3 the run is stopped if
recorded spend reaches the ceiling, and not for any other reason than a
technical failure.

## Archived requests

`scripts/archive_run_payload.py` records the exact create request the Prime
CLI 0.8.0 builds for a config, with every network write blocked (nothing is
sent; `scripts/test_archive_payload.py` checks that no write reaches the
transport). Archived: `results/training/run1/payload-cad-spec-9b-smoke.json`
(this smoke test's config, unchanged since the run) and
`results/training/run1/payload-cad-spec-9b.json` (the training run).
