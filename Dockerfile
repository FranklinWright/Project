# Build frontend (matches Makefile: bun install, bunx vite build, python inject)
FROM oven/bun:debian AS frontend-builder
WORKDIR /build

# Python for inject-ssr-template.py (same as Makefile)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && pip3 install --break-system-packages beautifulsoup4 \
    && rm -rf /var/lib/apt/lists/*

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY frontend ./frontend
COPY vite.config.ts ./
COPY tsconfig*.json ./

RUN bun run build && bun run build:ssr

COPY scripts/inject-ssr-template.py ./scripts/inject-ssr-template.py
RUN python3 scripts/inject-ssr-template.py

# Use the Lambda adapter extension.
FROM public.ecr.aws/awsguru/aws-lambda-adapter:0.9.0 AS aws-lambda-adapter

# Runtime image aligned with Flask backend.
FROM python:3.11-slim
WORKDIR /app

# Copy the Lambda adapter.
COPY --from=aws-lambda-adapter /lambda-adapter /opt/extensions/lambda-adapter

# Install Node.js for SSR subprocess
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# App code and built frontend
COPY backend ./backend
COPY --from=frontend-builder /build/dist ./dist

# Lambda adapter expects app on port 8080
ENV PORT=8080
EXPOSE 8080

# --chdir backend so "from models" resolves; PROJECT_ROOT still correct (parent of backend)
CMD ["gunicorn", "--chdir", "backend", "-b", "0.0.0.0:8080", "-w", "2", "--timeout", "120", "app:app"]
