# Application environment variables

- **`SECRET_KEY`** - django SECRET_KEY from settings
- **`DEBUG`** - 1 or 0. Debug mode in Django
- **`DATABASE_URL`** - URL in the format of [dj-database-url](https://github.com/jazzband/dj-database-url/#url-schema)
- **`RUN_MIGRATIONS`** - Flag to run migratioins or not. Set 1 to run migrations while container starting.
- **`CREATE_SUPERUSER`** - Flag to create superuser or not. Set 1 to createsuperuser while container starting. Also must set another superuser environment variables, look next.
- **`DJANGO_SUPERUSER_PASSWORD`** - superuser password. Need it and it is applied only when CREATE_SUPERUSER=1
- **`DJANGO_SUPERUSER_USERNAME`** - superuser username.  Need it and it is applied only when CREATE_SUPERUSER=1
- **`DJANGO_SUPERUSER_EMAIL`** - superuser email. Need it and it is applied only when CREATE_SUPERUSER=1
<!-- - **`PROMETHEUS_MULTIPROC_DIR`** - Path for prometheus databases, where prometheus metrics are stored. Needs for multiple workers. Details [here](https://github.com/prometheus/client_python/blob/master/README.md#multiprocess-mode-eg-gunicorn). Default value in docker image is /app/src/prometheus_metrics. -->
- **`AMOCRM_ENTITIES_ENDPOINT_AUTH_KEY`** - Auth key for third-party server requests for fetching amoCRM entities for salary calculating
- **`SALARIES_DASHBOARD_AUTH_KEY`** - Auth key for access to salaries dashboard on application server on page https://{{hostname}}/salaries/sales-plan-progress?auth_key={{AUTH_KEY}}.

For docker environment variables look [Docker section](#Docker-container-environment-variables)

# Preparing before first launch on local machine

## Install dependencies

```
$ poetry install
```

## Activate virtual environment shell

```
$ poetry shell
```

## Set environment variables

<br>
Create .env file in folder and set necessary values for env variables
<br><br>

## Collect static and make migrations

```
$ poetry run python manage.py collectstatic --no-input
$ poetry run python manage.py migrate --no-input
$ poetry run python manage.py createsuperuser
``` 

# Starting server

```
$ make runserver
```

# Linting

```
$ make lint
```

# Testing

```
$ make test
```

# Testing with code coverage

```
$ make test-coverage
```

<br>

# Docker run

## Before run

Here is a [docker-compose.yml](docker-compose.yml) config example, which is actually ready for local machine launch. 

Before launch you need to do next. It's optional, but you should know about it:

*Set env variables in docker-compose.yml (parameter [**environment**](https://docs.docker.com/compose/compose-file/compose-file-v3/#environment)), or create .env file in the root of project and fill it with actual env variables for docker containers. Don't forget about changing docker-compose.yml config for successfully apply .env file params (parameter [**env_file**](https://docs.docker.com/compose/compose-file/compose-file-v3/#env_file)) for each service*


## Docker container environment variables

All application environment variables + below:

- **`G_NUM_OF_WORKERS`** - Number of workers on Gunicorn
- **`G_WORKER_TIMEOUT`** - Gunicorn worker request timeout
- **`G_WORKER_CONNECTIONS`** - Number of connnections per one Gunicorn worker
- **`G_PORT`** - Port listened by Gunicorn

## Run
```
$ docker-compose up
```

<br>

# Docker build

To rebuilding image to the last code version, you have to:

1. Run `docker-compose build` command. Wait for rebuilding.
1. `docker-compose up` again to up services with new images.