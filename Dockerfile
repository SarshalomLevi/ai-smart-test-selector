# =========================
# Stage 1: Builder
# =========================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# install deps into wheel cache
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# =========================
# Stage 2: Runtime
# =========================
FROM python:3.11-slim

WORKDIR /app

# system minimal runtime deps only
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# copy wheels from builder
COPY --from=builder /wheels /wheels
COPY requirements.txt .

RUN pip install --no-cache-dir /wheels/*

# copy source code
COPY . .

# IMPORTANT for your structure
ENV PYTHONPATH=/app/src

# optional but recommended
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# production server config
CMD ["uvicorn", "ai_smart_test_selector.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
