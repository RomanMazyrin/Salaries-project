runserver:
	docker-compose up
	
lint:
	autopep8 --in-place --recursive src
	flake8 src