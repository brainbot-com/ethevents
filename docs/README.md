# Welcome to the documentation for eth.events

The documentation is served at http://ethevents.readthedocs.io
and is build with the Readthedocs / Sphinx python packages.

#  Development

Build instructions for the documentation:

Prerequisites: python3, pip

in ethevents/docs do the following:

	make pip-install
	make html


After building the documentation, to serve it locally, execute the following in the terminal:

	cd _build/html
	python3 -m http.server 8080
	# then in your browser, visit http://localhost:8080
