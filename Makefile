#
# Project makefile for a Common Tango classes for tmc project. You should normally only need to modify
# PROJECT below.
#
PROJECT = ska-tmc-common

# Issue resolution with twine during publish
python-pre-publish:
	pip3 install twine

#DAR101 Missing parameter(s) in Docstring: - fqdn
#DAR201 Missing "Returns" in Docstring: - return
#DAR301 Missing "Yields" in Docstring: - yield
#DAR401 Missing exception(s) in Raises section: -r Exception
PYTHON_SWITCHES_FOR_FLAKE8=--ignore=DAR101,DAR201,DAR103,DAR301,W503,DAR003
MARK ?=
PYTHON_VARS_AFTER_PYTEST ?= --count=50 -m '$(MARK)' $(ADD_ARGS) $(FILE) -x 

# include makefile to pick up the standard Make targets, e.g., 'make build'
# build, 'make push' docker push procedure, etc. The other Make targets
# ('make interactive', 'make test', etc.) are defined in this file.
-include .make/base.mk
-include .make/python.mk
-include PrivateRules.mak