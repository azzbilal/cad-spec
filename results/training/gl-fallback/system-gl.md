# GL fallback and scoring check: system GL present, installed wheel

Run 2026-09-30 01:53:42 UTC with `gl_fallback_check.py --expect system --label system GL present, installed wheel --system-gl-note present (Ubuntu 24.04 packages) --out results/training/gl-fallback/system-gl`.

| Environment | |
|---|---|
| platform | `Linux-6.18.44-fc-v50-x86_64-with-glibc2.39` |
| machine | `x86_64` |
| glibc | `glibc-2.39` |
| python | `3.12.3` |
| cpus | `1` |
| cad_spec | `0.4.5` |
| cad_spec_path | `/tmp/v045/lib/python3.12/site-packages/cad_spec` |
| installed_wheel | `True` |
| sandbox_mode | `fork` |
| system GL/X11 before the run | present (Ubuntu 24.04 packages) |

| Startup (fresh process, `require_cadquery`) | |
|---|---|
| ok | True |
| cadquery | 2.8.0 |
| gl_source | system |
| seconds | 1.37 |
| peak_rss_mb | 445 |

| Scoring through verifiers | Result |
|---|---|
| reference_binary | 1.0 |
| l4_failure_binary | 0.0 |
| l4_failure_continuous | 0.7778 |
| full_rollout_reward | 1.0 |
| full_rollout_error | None |

| Concurrent answers | Wall (s) | Median call (s) | Max call (s) | Rewards matching screening | All-pass |
|---|---|---|---|---|---|
| 1 | 0.06 | 0.059 | 0.06 | 1/1 | 1 |
| 8 | 0.49 | 0.059 | 0.11 | 8/8 | 6 |
| 32 | 1.8 | 0.057 | 0.1 | 32/32 | 24 |
| 64 | 3.5 | 0.057 | 0.1 | 64/64 | 40 |

**Gate: PASS.**
