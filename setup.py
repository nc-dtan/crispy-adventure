from setuptools import setup, find_packages
from Cython.Distutils import build_ext


setup(
	maintainer='ICI - Supernova',
    name='psrm',
	version='0.1',
	long_description='',
	license='',
    packages=find_packages(),
    url='https://github.com/nc-dtan/crispy-adventure',
    cmdclass={'build_ext': build_ext},
)

