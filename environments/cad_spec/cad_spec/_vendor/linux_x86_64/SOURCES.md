# Vendored GL and X11 runtime libraries (Linux x86_64)

Loaded only when the system has no libGL.so.1 / libX11.so.6 (see
`_ensure_gl_libraries` in `cad_spec/measure.py`). OpenCascade's OCP binding
links them at load time; cad-spec never renders. Ubuntu 20.04 builds, so they
need glibc >= 2.26 at most. Licences: `licenses/` (from each package).

| Package | Version | .deb SHA-256 | Source |
|---|---|---|---|
| libbsd0 | 0.10.0-1 | `4f668025fe923a372eb7fc368d6769fcfff6809233d48fd20fc072917cd82e60` | http://archive.ubuntu.com/ubuntu/pool/main/libb/libbsd/libbsd0_0.10.0-1_amd64.deb |
| libgl1 | 1.3.2-1~ubuntu0.20.04.2 | `bf37a7087ce67518b0d1e377c9058ef19db431599cec653a743e8379fa1a4a37` | http://archive.ubuntu.com/ubuntu/pool/main/libg/libglvnd/libgl1_1.3.2-1~ubuntu0.20.04.2_amd64.deb |
| libglvnd0 | 1.3.2-1~ubuntu0.20.04.2 | `df7ebdaef90e7e912147f5dd2f6568759b9111890b61936443a8b1fde1982655` | http://archive.ubuntu.com/ubuntu/pool/main/libg/libglvnd/libglvnd0_1.3.2-1~ubuntu0.20.04.2_amd64.deb |
| libglx0 | 1.3.2-1~ubuntu0.20.04.2 | `2620a3da6755af5df028a6f48c56e754ce90eef58c201dc9a289d5736eaad0c4` | http://archive.ubuntu.com/ubuntu/pool/main/libg/libglvnd/libglx0_1.3.2-1~ubuntu0.20.04.2_amd64.deb |
| libx11-6 | 2:1.6.9-2ubuntu1.6 | `20d7c0a8ea7a138d49d777a5db8e652071a3c47c78136450ec7417b5232b84ac` | http://archive.ubuntu.com/ubuntu/pool/main/libx/libx11/libx11-6_1.6.9-2ubuntu1.6_amd64.deb |
| libxau6 | 1:1.0.9-0ubuntu1 | `58a0d78302a35e4584f96cd598af16b563ae7aae4af589e2a7cee6dc6666d979` | http://archive.ubuntu.com/ubuntu/pool/main/libx/libxau/libxau6_1.0.9-0ubuntu1_amd64.deb |
| libxcb1 | 1.14-2 | `3fcab5cc6a70bcb1e4157748f9c626be21bc18b4c8459447e4c213cba98b9831` | http://archive.ubuntu.com/ubuntu/pool/main/libx/libxcb/libxcb1_1.14-2_amd64.deb |
| libxdmcp6 | 1:1.1.3-0ubuntu1 | `8a612b0fb60a41b92698f87258bc5ec6467da88e38d3de79411e02921c42af87` | http://archive.ubuntu.com/ubuntu/pool/main/libx/libxdmcp/libxdmcp6_1.1.3-0ubuntu1_amd64.deb |

| File | SHA-256 |
|---|---|
| libbsd.so.0 | `f660c0d2fba4d82d7866af4d174a33bf3de8dfb3632267662db74c33013c0913` |
| libXdmcp.so.6 | `a65f7757d765b8eeb15fea3db8b66da969fa10e44264fcf01f7ab19a1dbd0d24` |
| libXau.so.6 | `2a883844bd6b9507467f372d8a46ddc55edef5ea87e1c63c75e08fb7c939beb1` |
| libxcb.so.1 | `29965900a4ad6fdee5ca5272ef0c91f517c7e7d67829bef7b73a5546637d16a8` |
| libX11.so.6 | `04de566fe59e577bbfb531f01c5c171af5cd46a4ef0f471ea9e48df0a7bca515` |
| libGLdispatch.so.0 | `80f42924c9ee8e5c08e469ce53e50463b47e50177a828c8aa4a672b8662ed7c9` |
| libGLX.so.0 | `74c0d009f5b67172ea84f308be4754b90b6f6302c56b7cc747e95eb17937b7eb` |
| libGL.so.1 | `887514c6156db32ca306debe372c295094a6a8c7bfd082f7bfc7fb01411ee06c` |

## Provenance check (30 September 2026)

Chain verified from Ubuntu's signing key to each file: `gpgv` with
`/usr/share/keyrings/ubuntu-archive-keyring.gpg` reports a good signature
("Ubuntu Archive Automatic Signing Key (2012)") on the `Release` files of
`focal` and `focal-updates`; the SHA-256 of each
`main/binary-amd64/Packages.gz` matches its `Release` entry; the SHA-256 of
each `.deb` above matches its `SHA256:` field in that index; the files were
extracted with `dpkg-deb -x` and their hashes recorded above.
`tests/test_gl_fallback.py` fails if a shipped file no longer matches.

