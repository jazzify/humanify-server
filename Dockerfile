# Build stage
FROM python:3.12-slim AS builder

# Set environment variables
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    python3-dev \
    libpq-dev \
    build-essential \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install UV securely with checksum verification
RUN curl -sSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.uv/bin:$PATH"

# Set up dependencies
WORKDIR /build
COPY pyproject.toml ./
COPY uv.lock ./

# Install dependencies with UV
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -e .

# Final stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1


# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Expose port
EXPOSE 80

# Run the application (using gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "3", "--timeout", "120", "humanify_project.wsgi:application"]
