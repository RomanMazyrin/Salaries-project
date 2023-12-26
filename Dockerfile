FROM python:3.11-alpine

LABEL org.opencontainers.image.source="https://github.com/RomanMazyrin/Salaries-project"

# Create separate user
RUN addgroup --system app && adduser -S -G app app
USER app

WORKDIR /home/app

ENV \
    # Adding folder with poetry to PATH so poetry can be called
    PATH="/home/app/.local/bin:$PATH" \
    # Python
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Poetry
    POETRY_VERSION="1.6.1" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR="/tmp/poetry_cache" \
    # Gunicorn
    G_PORT=8000 \
    G_NUM_OF_WORKERS=2 \
    G_WORKER_TIMEOUT=60 \
    G_WORKER_CONNECTIONS=1000


# Install poetry
COPY --chown=app:app install_poetry.py .
RUN python install_poetry.py


# Install application python dependencies
COPY --chown=app:app pyproject.toml poetry.lock ./
RUN poetry install && rm -rf $POETRY_CACHE_DIR

# Copy entrypoint script
COPY --chown=app:app entrypoint.sh .

# Copy project files
COPY --chown=app:app . .

# Collect static
RUN poetry run python manage.py collectstatic --no-input

CMD [ "./entrypoint.sh" ]