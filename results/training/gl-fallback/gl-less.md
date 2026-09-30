# GL fallback and scoring check: gl-less (system GL/X11 hidden), installed wheel

Run 2026-09-30 01:53:28 UTC with `gl_fallback_check.py --expect vendored --label gl-less (system GL/X11 hidden), installed wheel --system-gl-note hidden: libGL, libGLX, libGLdispatch, libX11, libxcb, libXau, libXdmcp moved out of /usr/lib/x86_64-linux-gnu --out results/training/gl-fallback/gl-less`.

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
| system GL/X11 before the run | hidden: libGL, libGLX, libGLdispatch, libX11, libxcb, libXau, libXdmcp moved out of /usr/lib/x86_64-linux-gnu |

| Startup (fresh process, `require_cadquery`) | |
|---|---|
| ok | True |
| cadquery | 2.8.0 |
| gl_source | vendored |
| seconds | 1.29 |
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
| 1 | 0.06 | 0.064 | 0.06 | 1/1 | 1 |
| 8 | 0.56 | 0.066 | 0.11 | 8/8 | 6 |
| 32 | 1.76 | 0.056 | 0.11 | 32/32 | 24 |
| 64 | 3.59 | 0.058 | 0.1 | 64/64 | 40 |

**Gate: PASS.**
