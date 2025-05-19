FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE humanify_project.settings.prod

RUN groupadd -r appgroup
RUN useradd --no-log-init -m -r -g appgroup appuser

WORKDIR /code

RUN pip install uv

COPY pyproject.toml ./
RUN uv sync --no-dev --no-cache

COPY . .

RUN chown -R appuser:appgroup /code

USER appuser

RUN uv run python manage.py collectstatic --noinput

EXPOSE 80

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:80", "humanify_project.wsgi:application"]
