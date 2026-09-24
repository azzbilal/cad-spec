# Threat model and execution safety

cad-spec executes model-generated Python: the score comes from the solid the
code builds. This page states what is isolated, what is not, on which
platform, and which setup to use when. Guarantees below are stated per mode;
where a protection is *requested* but not *verified* at runtime, it says so.

## Who is trusted

| Party | Trusted? |
|---|---|
| You, the person running the scorer | yes |
| The cad-spec source code | yes |
| The completion a model returned (`result = ...`) | **no** |

A model under RL training is an optimiser. It can and will stumble into code
that hangs, eats memory, writes files, monkeypatches libraries, or games the
measurement. The design must not rely on that being accidental.

## The trust boundary (since 0.4.0)

Model code never hands the scorer a Python object.

1. **Untrusted side** (`build_brep`): execute the code, take the OCCT kernel
   shape wrapped by each CadQuery object bound to `result`, and serialise it
   to **BREP**, OpenCascade's plain-text geometry format.
2. **Trusted side** (`load_brep` + `measure`): parse the BREP bytes with the
   kernel and measure what they describe.

No method of the model's objects is ever called to describe geometry, and
nothing is unpickled from a rollout. Before 0.4.0, an object whose
`BoundingBox()` and `Volume()` returned nominal numbers scored 1.0 while its
real geometry was a 1 mm cube, and fork mode returned results as a pickle,
which can execute code when loaded. Both paths are gone; regression cases
`HACK_fake_result_object` and `test_fake_result_object_through_the_sandbox`
pin it.

What still crosses back from a rollout: one status byte, then either BREP
bytes (max 8 MB, parsed as data) or an error message (max 300 characters,
control characters stripped, treated as data and shown in reports).

## Execution modes

| | `fork` (default Linux, macOS) | `reuse` (default Windows) | `inproc` (`CAD_SPEC_INPROC=1`) | container (`Dockerfile`) |
|---|---|---|---|---|
| Fresh process per rollout | yes, forked from a warm worker (~60 ms) | no, one persistent worker | no, your process | yes (fork inside) |
| Measured in | the trusted worker, from BREP bytes | the rollout's own process | your process | the trusted worker |
| Python state isolated between rollouts | yes | **no** | **no** | yes |
| Environment scrubbed | yes: keeps only `PATH`, `LANG`, `LC_ALL`, `PYTHONHASHSEED`, `SYSTEMROOT`, `TMP`, `TEMP`; `HOME`/`TMPDIR` point at the rollout dir | no | no | yes, nothing to leak |
| Inherited file descriptors | all closed except the result pipe | inherited | inherited | as fork |
| Descendant processes | own process group, SIGKILLed when the rollout ends | not tracked | not tracked | as fork, plus `--pids-limit` |
| Wall-clock bound | yes, enforced by the worker; outer backstop kills a wedged worker | yes, the parent kills the whole worker | **none** | as fork |
| CPU time, file size, open files | rlimits: budget + 1 s CPU, 16 MB files, 64 fds | none | none | as fork, plus cgroups |
| Memory | Linux: address-space rlimit of current size + `CAD_SPEC_MEM_MB` (default 2048). **macOS: none** (no `/proc`) | none | none | `--memory` cgroup |
| Network | best-effort user + network namespace; **not verified at runtime**; unavailable where unprivileged namespaces are disabled | open | open | none (`--network none`) |
| Per-rollout temp dir | yes, deleted after | yes, deleted after unless the worker is killed mid-rollout | **no** | yes |
| Use for | local training and evals | Windows development, trusted models only | stepping through the scorer in a debugger | untrusted output at scale, sharing with others |

`python -m cad_spec sandbox` prints the requested configuration for the next
rollout, and every run file written by `scripts/run_baseline.py` records it.
These are the limits *requested*; the child cannot report back reliably what
actually applied, because it is untrusted once model code runs.

## What `fork` mode does NOT stop

- **Reading your files.** The child runs as your user. Code that opens
  `~/.ssh/id_ed25519` with an absolute path can read it. It can only send it
  somewhere if the network namespace failed to apply, and it can only return
  it to you inside a 300-character error message. Do not run untrusted output
  on a machine whose files you would not show the model.
- **Writing outside the temp dir** with absolute paths, up to 16 MB per file.
- **Kernel, CPython or OpenCascade exploits**, including a malicious BREP
  aimed at the parser. A parser crash kills the worker, which respawns; it is
  not a sandbox escape, but a parser *exploit* is out of scope. Use the
  container or a VM.

## The container

The `Dockerfile` alone does not isolate anything; the `docker run` flags do.
Use them all:

```bash
docker run --rm --network none --read-only --tmpfs /tmp:size=64m \
  --memory 2g --pids-limit 128 --cpus 1 --cap-drop ALL \
  --security-opt no-new-privileges \
  -v "$PWD/answer.py:/in/answer.py:ro" cad-spec score gen-0001 /in/answer.py
```

The base image (`python:3.12-slim`) and apt packages float; rebuild from a
pinned digest if you need bit-identical images. CI builds the image and scores
a reference answer inside it with these flags; it does not attempt hostile
code.

## Verified behaviour

`environments/cad_spec/tests/test_measure.py` pins, on POSIX (fork mode):

- a fabricated result object is measured by its real geometry;
- a rollout that monkeypatches `cadquery` cannot affect the next rollout;
- a parent environment variable is invisible to a rollout;
- the rollout sees no inherited file descriptors beyond its own;
- a background process started by model code dies with the rollout, and does
  not delay it;
- `CAD_SPEC_MEM_MB` is honoured (0.3.x silently ignored it);
- a relative-path write does not survive the rollout;
- a 64 GB allocation fails cleanly and the next rollout still scores;
- a 64 MB file write fails on the file-size limit;
- an infinite loop is killed at the budget and the worker keeps serving.

On Windows those tests are skipped: reuse mode does not make those claims.

## Reporting a problem

Open an issue with a minimal answer file that escapes a limit above. Do not
include working exploits against third-party systems.
