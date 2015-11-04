from setuptools import setup, find_packages

setup(
	name="scale",
	version="0.1.0",
	description="Scalable language engineering toolkit",
	longdescription=open("README.md").read(),

	packages=find_packages(),

	author="Joris Pelemans",
	author_email="joris@pelemans.be",

	url="https://github.com/jorispelemans/scale",

	install_requires=[
		"gensim",
	],

	include_package_data=True,
)
