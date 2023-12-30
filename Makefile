runserver:
	poetry run gunicorn -w=2 -k=gevent --worker-connections=1000 -t=60 --bind 0.0.0.0:80 --reload salaries.wsgi
	
lint:
	poetry run black .
	poetry run flake8 .
	poetry run isort .

test:
	poetry run pytest -s tests/

test-coverage:
	poetry run pytest -s --cov --cov-report term --cov-fail-under=70 tests/

collectstatic:
	poetry run python manage.py collectstatic --no-input