FROM python:3.11-slim AS build

# python-fontconfig is only published as an sdist, so it is compiled against
# the system fontconfig (and freetype) headers.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libfontconfig-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN DJANGO_DEBUG=false DJANGO_SECRET_KEY=collectstatic \
    /app/.venv/bin/python manage.py collectstatic --noinput


FROM python:3.11-slim

# Runtime fontconfig library plus a few font families for FontListView.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libfontconfig1 fonts-dejavu-core fonts-liberation2 fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --system --create-home app
WORKDIR /app
COPY --from=build --chown=app:app /app /app
USER app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=false

EXPOSE 8000
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]
