# Disposable scoring sandbox for UNTRUSTED model output.
#
#   docker build -t cad-spec .
#   docker run --rm --network none --read-only --tmpfs /tmp:size=64m \
#     --memory 2g --pids-limit 128 --cpus 1 --cap-drop ALL \
#     --security-opt no-new-privileges \
#     -v "$PWD/answer.py:/in/answer.py:ro" cad-spec score gen-0001 /in/answer.py
#
# The container adds what the in-process sandbox cannot: no network by
# construction, a read-only filesystem, no host files except the one answer
# mounted read-only, no secrets, and kernel-enforced memory/process caps.
# Inside it, the fork sandbox still gives every rollout a fresh process.
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libxrender1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/cad-spec
COPY environments/cad_spec/constraints.txt environments/cad_spec/pyproject.toml ./
COPY environments/cad_spec/README.md ./
COPY environments/cad_spec/cad_spec ./cad_spec
RUN pip install --no-cache-dir -c constraints.txt .

RUN useradd --create-home --uid 10001 scorer
USER scorer
ENV CAD_SPEC_SANDBOX=fork \
    CAD_SPEC_EXEC_TIMEOUT=10 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/tmp
ENTRYPOINT ["cad-spec"]
CMD ["sandbox"]
