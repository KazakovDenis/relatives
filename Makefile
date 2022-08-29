run:
	uvicorn main:app

lint:
	flake8
	isort .
