# =========================
# Builder
# =========================
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    git \
    ca-certificates \
    libssl-dev \
    libffi-dev \
    libsecp256k1-dev \
    autoconf \
    automake \
    libtool \
    m4 \
    perl \
    && rm -rf /var/lib/apt/lists/*

# Guarantee versioned autotools wrappers expected by secp256k1 sdist
RUN set -eux; \
    command -v aclocal; \
    command -v automake; \
    if ! command -v aclocal-1.16; then ln -s "$(command -v aclocal)" /usr/bin/aclocal-1.16; fi; \
    if ! command -v automake-1.16; then ln -s "$(command -v automake)" /usr/bin/automake-1.16; fi; \
    command -v aclocal-1.16; \
    command -v automake-1.16

WORKDIR /app
RUN pip install --no-cache-dir uv

COPY ./agent/pyproject.toml ./agent/uv.lock ./

RUN uv venv /opt/venv \
 && . /opt/venv/bin/activate \
 && uv sync --active --frozen --no-dev

COPY ./agent ./
RUN . /opt/venv/bin/activate && uv pip install -e .

# =========================
# Runtime
# =========================
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl-dev \
    libffi-dev \
    libsecp256k1-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv
COPY ./agent ./

RUN useradd --create-home --shell /bin/bash app \
 && chown -R app:app /app
USER app

CMD ["python", "src/main.py"]