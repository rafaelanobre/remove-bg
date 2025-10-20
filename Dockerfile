FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Install system dependencies required by rembg and Pillow
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.9.4 /uv /uvx /bin/

COPY pyproject.toml uv.lock /_lock/

RUN --mount=type=cache,target=/root/.cache \
    cd /_lock && \
    uv sync \
    --frozen \
    --no-install-project \
    --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache \
    uv sync --frozen --no-dev

# Pre-download the rembg AI model during build
RUN /app/.venv/bin/python -c "from rembg import remove; from PIL import Image; import io; \
    img = Image.new('RGB', (100, 100), color='white'); \
    buf = io.BytesIO(); \
    img.save(buf, format='PNG'); \
    buf.seek(0); \
    remove(buf.read());"

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/app/.venv/bin/gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "remove_bg.wsgi:application"]