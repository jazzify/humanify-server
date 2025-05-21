FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE humanify_project.settings.prod

WORKDIR /code

EXPOSE 80

RUN pip install uv

COPY pyproject.toml ./
RUN uv sync --no-dev --no-cache

COPY . .

FROM base AS production

RUN groupadd -r appgroup && \
    useradd --no-log-init -m -r -g appgroup appuser && \
    chown -R appuser:appgroup /code

USER appuser
RUN uv run python manage.py collectstatic --noinput

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:80", "humanify_project.wsgi:application"]

FROM base AS development

RUN uv run python manage.py collectstatic --noinput

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:80", "humanify_project.wsgi:application"]
