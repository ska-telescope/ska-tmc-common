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

#
# include makefile to pick up the standard Make targets, e.g., 'make build'
# build, 'make push' docker push procedure, etc. The other Make targets
# ('make interactive', 'make test', etc.) are defined in this file.
#

-include .make/python.mk
-include .make/oci.mk
-include .make/docs.mk
-include .make/release.mk
-include .make/make.mk
-include .make/help.mk
-include PrivateRules.mak
-include temp/test.mk



.PHONY: all test lint help