ipython:
	PYTHONPATH=src pipenv run ipython

test:
	PYTHONPATH=src pipenv run pytest

white:
	pipenv run white ./tests/*.py
	pipenv run white ./src/

update:
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv update --dev
	PIPENV_IGNORE_VIRTUALENVS=1 pipenv lock -r --dev-only > dev-requirements.txt


#----------
# clean
#----------

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .cache
	rm -fr .mypy_cache
	rm -fr .pytest_cache
	rm -f .coverage
	rm -fr htmlcov/

#----------
# publish
#----------

publish: do_publish clean

do_publish:
	pipenv run python setup.py sdist
	pipenv run python setup.py bdist_wheel --universal
	twine upload -r pypi dist/*
