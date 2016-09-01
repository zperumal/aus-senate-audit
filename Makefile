.PHONY: docs clean

docs:
	cd docs; sphinx-build -b html -d build/doctrees source build/html

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
