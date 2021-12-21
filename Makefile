#
# Project makefile for a Common Tango classes for tmc project. You should normally only need to modify
# PROJECT below.
#

#
# CAR_OCI_REGISTRY_HOST and PROJECT are combined to define
# the Docker tag for this project. The definition below inherits the standard
# value for CAR_OCI_REGISTRY_HOST = artefact.skao.int and overwrites
# PROJECT to give a final Docker tag of
# artefact.skao.int/ska-telescope/ska-tmc-common
#

# DOCKER_REGISTRY_USER:=ska-telescope

CAR_OCI_REGISTRY_HOST ?= artefact.skao.int
CAR_OCI_REGISTRY_USER ?= ska-telescope
PROJECT = ska-tmc-common


#DAR101 Missing parameter(s) in Docstring: - fqdn
#DAR201 Missing "Returns" in Docstring: - return
#DAR301 Missing "Yields" in Docstring: - yield
#DAR401 Missing exception(s) in Raises section: -r Exception
PYTHON_SWITCHES_FOR_FLAKE8=--ignore=DAR101,DAR201,DAR301,DAR401,W503 --max-line-length=180


#
# include makefile to pick up the standard Make targets, e.g., 'make build'
# build, 'make push' docker push procedure, etc. The other Make targets
# ('make interactive', 'make test', etc.) are defined in this file.
#

-include .make/*.mk

-include PrivateRules.mak