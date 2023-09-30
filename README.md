# Application environment variables

- **`SECRET_KEY`** - django SECRET_KEY from settings
- **`DEBUG`** - 1 or 0. Debug mode in Django
- **`DB_ENGINE`** - Engine for database in Django. Default is 'django'.db.backends.sqlite'
- **`DB_DATABASE`** - Database name or path (if sqlite)
- **`DB_USER`** - Database user name
- **`DB_PASSWORD`** - Database user password
- **`DB_HOST`** - Database host
- **`DB_PORT`** - Database port
- **`PROMETHEUS_MULTIPROC_DIR`** - Path for prometheus databases, where prometheus metrics are stored. Needs for multiple workers. Details [here](https://github.com/prometheus/client_python/blob/master/README.md#multiprocess-mode-eg-gunicorn). Default value in docker image is /app/src/prometheus_metrics.
- **`AMOCRM_ENTITIES_ENDPOINT_AUTH_KEY`** - Auth key for third-party server requests for fetching amoCRM entities for salary calculating
- **`SALARIES_DASHBOARD_AUTH_KEY`** - Auth key for access to salaries dashboard on application server on page https://{{hostname}}/salaries/sales-plan-progress?auth_key={{AUTH_KEY}}.

For docker environment variables look [Docker section](#Docker-container-environment-variables)

# Preparing before first launch on local machine

## Install dependencies

```
$ pip install -r requirements.txt
```

## Activate virtual environment shell

```
$ source bin/activate
```

## Activate pre-commit hooks

```
$ pre-commit install
```

## Set environment variables

<br>
Create .env file in src/ folder and set necessary values for env variables
<br><br>

## Collect static and make migrations

```
$ cd src
$ python manage.py collectstatic --no-input
$ python manage.py migrate --no-input
$ python manage.py createsuperuser
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

- **`NUM_OF_WORKERS`** - Number of workers on gunicorn
- **`WORKER_TIMEOUT`** - Gunicorn worker request timeout
- **`WORKER_CONNECTIONS`** - Number of connnections per one gunicorn worker
- **`PORT`** - Port listened by gunicorn

## Run
```
$ docker-compose up
```

<br>

# Docker build

To rebuilding image to the last code version, you have to:

1. Run `docker-compose build` command. Wait for rebuilding.
1. `docker-compose up` again to up services with new images.