install:
	python setup.py install

dep:
	pip install -r requirements.txt

test:
	pytest psrm