# UNTESTED kit (2026-10-11): reproducible environment for the exciton-fluid project (CPU; add a CUDA base image for GPU jobs).
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git ca-certificates python3 python3-pip python3-venv pkg-config libssl-dev texlive-latex-extra latexmk \
    && rm -rf /var/lib/apt/lists/*
# Lean via elan, pinned toolchain
RUN curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain leanprover/lean4:v4.34.1
ENV PATH=/root/.elan/bin:/root/.cargo/bin:$PATH
# Rust
RUN curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal
WORKDIR /work
COPY requirements-exciton.txt /work/requirements-exciton.txt
RUN python3 -m pip install --break-system-packages -r requirements-exciton.txt
# the repository is mounted at /work/repo at run time; results are written to /work/out
CMD ["bash"]
