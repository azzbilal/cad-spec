"""0.4.5: CadQuery must load where the system has no libGL / libX11.

Smoke run jkqd5k12g1g5kvqyhmfg012k (30 Sep 2026): the Hosted Training
environment image lacks libGL.so.1, OCP links it at load time (even the
novtk build: TKOpenGl, TKService), and every rollout was scored 0 in silence.
The GL-less condition itself was reproduced by hiding the system libraries
(root needed, not repeatable in CI); these tests pin what CI can check.
"""

import ctypes
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from cad_spec import measure
from cad_spec.environment import load_environment

VENDOR = Path(measure.__file__).resolve().parent / "_vendor" / "linux_x86_64"
linux = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="the vendored libraries are Linux x86_64")


def test_every_vendored_library_is_shipped_with_its_recorded_hash():
    manifest = (VENDOR / "SOURCES.md").read_text(encoding="utf-8")
    for name in measure._VENDORED_GL:
        data = (VENDOR / name).read_bytes()
        assert data[:4] == b"\x7fELF", name
        assert hashlib.sha256(data).hexdigest() in manifest, f"{name} does not match SOURCES.md"
    assert len(list((VENDOR / "licenses").glob("*.copyright"))) == 8


@linux
def test_vendored_set_loads_by_path_in_a_fresh_process():
    """Loading the vendored copies by path, in dependency order, succeeds on
    this machine (CI: Ubuntu), whatever the system provides."""
    code = (
        "import ctypes, os, sys\n"
        f"d = {str(VENDOR)!r}\n"
        f"for n in {measure._VENDORED_GL!r}:\n"
        "    ctypes.CDLL(os.path.join(d, n), mode=ctypes.RTLD_GLOBAL)\n"
        "print('ok')\n"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    assert out.stdout.strip() == "ok", out.stderr


@linux
def test_vendored_libraries_need_at_most_glibc_2_26():
    """Ubuntu 20.04 builds: they must load on any image from glibc 2.26 up."""
    worst = (0, 0)
    for name in measure._VENDORED_GL:
        for major, minor in re.findall(rb"GLIBC_(\d+)\.(\d+)", (VENDOR / name).read_bytes()):
            worst = max(worst, (int(major), int(minor)))
    assert worst <= (2, 26), worst


def test_loader_reports_where_gl_came_from():
    where = measure._ensure_gl_libraries()
    if sys.platform.startswith("linux"):
        assert where in ("system", "vendored")
    else:
        assert where == "not-linux"


def test_load_environment_fails_fast_when_the_scorer_cannot_run(monkeypatch):
    """No environment with a dead scorer: raise at load, never score 0 later."""
    import cad_spec.environment as env_mod

    def dead():
        raise measure.ScorerUnavailableError("CadQuery is not importable (libGL.so.1 missing)")

    monkeypatch.setattr(env_mod, "require_cadquery", dead)
    with pytest.raises(measure.ScorerUnavailableError):
        load_environment(tier=["L4"], hints=True, reward="binary")


def test_loader_changes_nothing_when_the_system_has_gl(monkeypatch):
    """Fallback only: with a system libGL, no vendored path is ever opened."""
    if not sys.platform.startswith("linux"):
        pytest.skip("Linux behaviour")
    opened = []
    real = ctypes.CDLL

    def spy(name, *a, **k):
        opened.append(str(name))
        return real(name, *a, **k)

    try:
        real("libGL.so.1")
    except OSError:
        pytest.skip("no system libGL on this machine")
    monkeypatch.setattr(ctypes, "CDLL", spy)
    assert measure._load_gl_libraries() == "system"
    assert not any(os.sep in n for n in opened)


def test_fallback_never_mixes_system_and_vendored_copies(monkeypatch):
    """Once the system libGL is missing, every load is a vendored file by full
    path, in dependency order; no library is looked up by bare name."""
    calls = []

    def fake_cdll(name, *a, **k):
        calls.append(str(name))
        if str(name) == "libGL.so.1":
            raise OSError("libGL.so.1: cannot open shared object file")
        return object()

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(ctypes, "CDLL", fake_cdll)
    import platform

    monkeypatch.setattr(platform, "machine", lambda: "x86_64")
    assert measure._load_gl_libraries() == "vendored"
    assert calls[0] == "libGL.so.1"
    assert calls[1:] == [str(VENDOR / n) for n in measure._VENDORED_GL]
