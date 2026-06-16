.PHONY: test coverage

test:
	. .venv/bin/activate && python manage.py test

coverage:
	. .venv/bin/activate && coverage run manage.py test && coverage report && coverage html
