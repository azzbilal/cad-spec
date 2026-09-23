# Threat model and execution safety

cad-spec executes model-generated Python. That is the task: the score comes
from the solid the code builds. This page states exactly what is isolated,
what is not, and which setup to use for which situation.

## Who is trusted

| Party | Trusted? |
|---|---|
| You, the person running the scorer | yes |
| The cad-spec source code | yes |
| The completion a model returned (`result = ...`) | **no** |

A model under RL training is an optimiser. It can and will stumble into code
that hangs, eats memory, writes files, or monkeypatches the libraries the
scorer relies on. Most of this is accidental; the sandbox must not depend on
that.

## Execution modes

| Mode | Where | Per-rollout process | Python state isolated | Env vars scrubbed | Network | Resource limits | Use for |
|---|---|---|---|---|---|---|---|
| `fork` (default on Linux/macOS) | `CAD_SPEC_SANDBOX=fork` | yes, forked from a warm worker, ~60 ms | yes | yes (keeps PATH, LANG only) | cut via user+net namespaces **when the kernel allows it** | CPU time, address space (`CAD_SPEC_MEM_MB`, default 2048), 16 MB max file, 64 open files | local training, evals |
| `reuse` (default on Windows) | `CAD_SPEC_SANDBOX=reuse` | no, one persistent worker | **no**: a rollout can alter state later rollouts see | no | not restricted | wall-clock timeout only | trusted debugging, Windows dev |
| `inproc` | `CAD_SPEC_INPROC=1` | no, runs in your process | no | no | not restricted | none | stepping through the scorer in a debugger |
| container | `Dockerfile` | yes (fork inside) | yes | yes, nothing to leak | none (`--network none`) | kernel cgroups + all of the above | **untrusted output at scale, sharing with others** |

In every mode: each rollout runs in a fresh temporary directory that is
deleted afterwards, and `CAD_SPEC_EXEC_TIMEOUT` (default 10 s) bounds it.

`python -m cad_spec sandbox` prints what the next rollout will get. Every
results file written by `scripts/run_baseline.py` records the same.

## What `fork` mode does NOT stop

- **Reading your files.** The child runs as your user. Code that opens
  `~/.ssh/id_ed25519` with an absolute path can read it. It cannot send it
  anywhere if the network namespace applied, and it cannot return it to you
  (only measurements cross back), but do not run untrusted output on a
  machine whose files you would not show the model.
- **Writing outside the temp dir** with absolute paths, up to 16 MB per file.
- **Network, on kernels that forbid unprivileged user namespaces** (some
  hardened distros, many CI containers). `sandbox_info()` cannot see whether
  the namespace call succeeded inside the child; test with a connect attempt
  if it matters to you.
- **Kernel or CPython exploits.** Out of scope; use the container or a VM.

## Verified behaviour

`environments/cad_spec/tests/test_measure.py` pins, on POSIX:

- a rollout that monkeypatches `cadquery` cannot affect the next rollout;
- an environment variable in the parent is invisible to a rollout;
- a relative-path write does not survive the rollout;
- a 64 GB allocation fails cleanly and the next rollout still scores;
- a 64 MB file write fails on the file-size limit;
- an infinite loop is killed at the budget and the worker keeps serving.

## Reporting a problem

Open an issue with a minimal answer file that escapes a limit above. Do not
include working exploits against third-party systems.
