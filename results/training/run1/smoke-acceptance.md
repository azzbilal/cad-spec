# Training run 1: smoke-test acceptance (step 5)

Run `k3rwpbbk5sio4936onuai7ok` (`configs/rl/cad-spec-9b-smoke.toml`), Prime
Hosted Training, Prime CLI 0.8.0. Created 2026-09-30 14:49:49, started
14:50:13, completed 14:56:10 (about 6 minutes, setup included). Status
COMPLETED, no error message, no failure analysis. Source of every figure:
`prime train get -o json`, `logs`, `metrics`, `distributions`, `usage` for
this run.

## Registered acceptance checks (pre-registration section 6.1)

| # | Check | Evidence | Verdict |
|---|---|---|---|
| 1 | The three environments load at the registered version | Run record: `cad-spec-L4`, `cad-spec-L2`, `cad-spec-L1-L3`, all `bazzouzi/cad-spec` version `0.4.5` (version id `s41pd72x99yh706fv3vnftl8`), args `reward = "binary"`, `hints = true`, tiers as registered, ratios 0.5 / 0.25 / 0.25; pre-batch filter `zero_advantage` enforced. Logs: environments ready with 200, 200 and 400 train tasks | pass |
| 2 | Temperature 0.7 | Sent: the Prime CLI passes `cfg.sampling.temperature` to `create_run` (`prime_cli/commands/rl.py:1827`) and writes `payload["temperature"]` (`prime_cli/api/rl.py:299-300`); displayed as 0.7 before launch. Not echoed back by the run record, the logs or the rollout records. Thinking off is consistent with the answer lengths (mean 356 output tokens, L4 minimum 89) | pass, as sent |
| 3 | Rewards of both 0 and 1 at every step | Trained-batch reward counts (0 / 1): step 1: 59 / 69; step 2: 70 / 58; step 3: 56 / 72; step 4: 54 / 74; step 5: 51 / 77. No trained sample with zero advantage at step 5 | pass |
| 4 | No scoring errors | `has_error` 0.0 in all three environments; "Error 0.0%" at every logged step; scoring time mean 0.07 s per answer (one 10 s first-call warm-up) | pass |
| 5 | Cost per step | Usage: training 589.78K tokens $0.35, inference input 892.29K $0.18, output 402.80K $0.24, total **$0.66** for 5 steps: **$0.132 per step**. Training tokens 589.78K / 5 = 118K per step = 128 trained answers x 925 tokens (measured mean) | pass |

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

Smoke tests so far: $0.00 (`b32pcagfy8t4bqf2lnc6dep7`), $0.00
(`jvryf7tsn20jw66cfxesbp08`), $0.03 (`jkqd5k12g1g5kvqyhmfg012k`), $0.66
(`k3rwpbbk5sio4936onuai7ok`): **$0.69**.

`max_steps = floor((15.00 - 0.69 - 0.50) / 0.132) = floor(104.6) = 104`
(at most 150; at least 30). Expected training cost 104 x $0.132 = $13.73,
total with the smoke tests $14.42, under the $15 ceiling.
