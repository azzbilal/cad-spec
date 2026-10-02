# Audit of `cad-spec-gl-fallback.bundle`

## Verdict

**Likely fixes the specific missing `libGL.so.1` loader failure, but not yet cleared for another paid smoke run.** Confidence: 85% for the loader fix, lower for complete Hosted Training behavior. The bundle is valid and contains one commit, `0340f48`, based on the audited `dbd7428`. No scoring checks, gates, thresholds, prompts, or task generation changed. The new 0.4.5 config cannot run as written yet: `env -u SSLKEYLOGFILE prime env status bazzouzi/cad-spec --plain` reported latest published version **0.4.4**.

## What I verified independently

| Check | Result |
|---|---|
| Bundle integrity and scope | `git bundle verify` passed. The diff changes the GL loader, a startup import check, tests, vendored ELF files, docs, and the environment version pins. `rubric.py`, `tasks.py`, and `prompts.py` have no diff. |
| Wheel packaging | An offline `uv build` produced `cad_spec-0.4.5-py3-none-any.whl`, SHA-256 `56e779f8c878b137a37116fa52dd8539dda2275d658b3abd6b7a79b054883d1d`. ZIP inspection found all eight shared libraries and eight copyright files in the wheel. The wheel is marked `py3-none-any` despite carrying Linux x86_64 binaries, a portability metadata weakness, though the loader guards by platform. |
| File integrity | SHA-256 of each bundled `.so` matches its entry in `SOURCES.md`. This checks the bundle against its own manifest, not the upstream Ubuntu `.deb` hashes or provenance. |
| Local verifiers regression | With the bundle source on `PYTHONPATH`, `pytest -q tests/test_gl_fallback.py tests/test_rollout_path.py` returned **11 passed, 3 skipped** on Windows. The skipped cases are the Linux-only loader checks. |
| GL-less Linux loader | In a cached Python 3.12, glibc 2.36 Linux container, `ctypes.CDLL('libGL.so.1')` failed with the same missing-file error seen on Prime. With the bundle mounted read-only, `measure._load_gl_libraries()` returned `vendored`, and `ctypes.CDLL('libGL.so.1')` then succeeded. This used no Prime service. |
| Complete CadQuery score | **Not independently verified here.** The cached container lacked CadQuery. Downloading its Linux OCP and transitive wheels was too slow; the disposable container was stopped and removed. The bundle's claimed reference score and 64-answer benchmark appear only in commit text and Amendment 3, without a runnable benchmark artifact. |

## Challenges to the bundle

1. **The actual Prime fix still needs an installed-wheel test in a GL-less Linux image.** The new code preloads libraries in commit `0340f48` at `environments/cad_spec/cad_spec/measure.py:137-189`. My Linux check establishes that `libGL.so.1` resolves, but it did not run `import cadquery`, `env.init_state`, a reference score, or the fork sandbox in that image. The bundle's `tests/test_gl_fallback.py` tests manifest hashes, library loading, and a mocked startup exception; it does not reproduce the missing-system-GL condition with CadQuery and verifiers. The reported 64-way, 7.2-second result in `training-run-1.md:208-214` has no saved command, results, or timings in the commit.
2. **0.4.5 is not published.** Both RL configs now point to `bazzouzi/cad-spec@0.4.5`, while the free `prime env status` query reports 0.4.4 as latest. Publishing is outside this audit's authorization. A run from these configs would fail environment resolution until 0.4.5 is published and its served wheel checked.
3. **Two registration claims exceed the evidence in the bundle.** Amendment 3 says *every group* was flat (`training-run-1.md:194`), but the stopped run exposes no group reward vectors or step-0 samples. Its env-server logs establish many main-reward import failures and verifiers' 0.0 substitution, which strongly explains the flat groups without enumerating them. The amendment also says Hosted Training offers no custom environment image (`training-run-1.md:199`); the bundle has no source for that service capability. Prime's [Hosted Training documentation](https://docs.primeintellect.ai/verifiers/training) describes configuration but does not establish that negative claim.
4. **The fallback is selective, not an isolated library set.** `measure.py:169-175` tries each system SONAME first, then its vendored copy. On an image with some, but not all, of these libraries, the process can mix system and Ubuntu 20.04 copies. This worked in one GL-less Debian container; compatibility with Prime's precise image remains unverified. The `py3-none-any` wheel also installs the ELF payload on other platforms, although the loader does not use it there.
5. **Fail-fast is a real improvement, with an unmeasured startup cost.** `environment.py:236` calls `require_cadquery()` before reporting the environment ready. If import still fails, this prevents verifiers from converting each later scorer exception into 0.0. It also imports the CadQuery/OCP kernel during environment loading in each server process; memory and startup time on Hosted Training have not been measured. The spawned scorer worker imports it again (`measure.py:904-912` in the base code).
6. **Provenance and compatibility bounds need their own check.** The eight file hashes match `SOURCES.md`, and the loader works on glibc 2.36. The asserted Ubuntu archive hashes, licences, and minimum glibc version were not independently checked against the downloaded `.deb` archives or on the exact Hosted Training image. This is a release verification item, not evidence that the present GL loader test failed.

## Minimum gate before spending

1. Install the **built 0.4.5 wheel** and pinned CadQuery/OCP dependencies in a Linux x86_64 image without system `libGL.so.1` and `libX11.so.6`. From a fresh process, confirm `require_cadquery()` succeeds and reports `vendored`; score a reference as 1.0 and a known L4 failure as 0.0 through `env.init_state` and `env.rubric.score_rollout`, using the default `fork` sandbox. Cost: $0 local.
2. Run saved screening answers at concurrency 1, 8, 32, and 64 in that image. Keep the command, per-call latency, wall time, and exact reward comparison as an audit artifact. Require 64/64 reward matches and completion within the previously proposed 120-second gate. Cost: $0 local.
3. Correct or qualify the two unsupported Amendment 3 claims, record the served-wheel hash and `verify_hub` result, and confirm Hub 0.4.5 exists before using either updated config. No push or publication was performed in this audit. A new paid smoke test still needs separate approval with its exact command and estimated cost.

## Audit limits and cleanup

No Hosted Training, evaluation, paid inference, push, commit, or publication occurred. The bundle was inspected in a scratch clone. The Linux loader test used a disposable container; it was stopped and removed after the full CadQuery dependency download proved slow. The source repository remained on `main` at `dbd7428`.
