sdist:
	rm -rf dist/*
	pipenv run python setup.py sdist bdist_wheel

install:
	pipenv install --dev

lint:
	pipenv run flake8
