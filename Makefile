runserver:
	cd src && gunicorn -w=2 -t=600 app.wsgi --bind 0.0.0.0:8000 --reload
	
lint:
	autopep8 --in-place --recursive src
	flake8 src

test:
	cd src && pytest -s