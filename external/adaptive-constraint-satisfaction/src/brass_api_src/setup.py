from setuptools import setup, find_packages


setup(
    name='brass_api',
    version='0.1',
    description='Classes and functions related to accessing orientDB, MDL standards.',
    author='Di Yao',
    author_email='di.yao@vanderbilt.edu',
    url='',
    license='',
	install_requires=[
		'pyorient',
		'lxml'
	],
    packages=find_packages(),
    data_files=[
        ('brass_api/include/mdl_xsd', ['brass_api/include/mdl_xsd/MDL_v1_0_0.xsd'])
        ]
)

