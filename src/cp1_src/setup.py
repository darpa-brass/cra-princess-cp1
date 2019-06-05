from setuptools import setup, find_packages


setup(
    name='cp1',
    version='RR1.5',
    description='Classes and functions used to satisfy CP1 requirements.',
    author='Tameem Samawi',
    author_email='tsamawi@cra.com',
    url='',
    license='',
    install_requires=[
		'pandas',
		'ortools',
        'numpy',
        'gurobipy'
	],
    packages=find_packages()
)
