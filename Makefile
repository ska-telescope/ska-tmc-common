PROJECT = ska-tmc-common
CI_REGISTRY ?= gitlab.com

CAR_OCI_REGISTRY_HOST:=artefact.skao.int
PROJECT = ska-tmc-common
KUBE_APP = ska-tmc-common
TELESCOPE ?= SKA-mid
#DAR101 Missing parameter(s) in Docstring: - fqdn
#DAR201 Missing "Returns" in Docstring: - return
#DAR301 Missing "Yields" in Docstring: - yield
#DAR401 Missing exception(s) in Raises section: -r Exception
PYTHON_SWITCHES_FOR_FLAKE8=--ignore=DAR101,DAR201,DAR103,DAR301,W503,DAR003
TANGO_HOST ?= tango-databaseds:10000 ## TANGO_HOST connection to the Tango DS
PYTHON_LINE_LENGTH ?= 79
CI_PROJECT_PATH_SLUG ?= ska-tmc-common
CI_ENVIRONMENT_SLUG ?= ska-tmc-common
CLUSTER_DOMAIN ?= cluster.local
K8S_TIMEOUT = 600s
ITANGO_DOCKER_IMAGE = $(CAR_OCI_REGISTRY_HOST)/ska-tango-images-tango-itango:9.5.0
SKA_TANGO_OPERATOR = true
# Set the specific environment variables required for pytest
PYTHON_VARS_BEFORE_PYTEST ?= PYTHONPATH=.:./src TANGO_HOST=$(TANGO_HOST) CLUSTER_DOMAIN=$(CLUSTER_DOMAIN)

MARK ?= ## What -m opt to pass to pytest
EXIT_AT_FAIL = true

FILE ?= tests## A specific test file to pass to pytest
ADD_ARGS ?= ## Additional args to pass to pytest

# KUBE_NAMESPACE defines the Kubernetes Namespace that will be deployed to
# using Helm.  If this does not already exist it will be created
KUBE_NAMESPACE ?= ska-tmc-common

# HELM_RELEASE is the release that all Kubernetes resources will be labelled
# with
HELM_RELEASE ?= test
HELM_CHARTS_TO_PUBLISH=

# UMBRELLA_CHART_PATH Path of the umbrella chart to work with
HELM_CHART=ska-tmc-common
UMBRELLA_CHART_PATH ?= charts/$(HELM_CHART)/
K8S_CHARTS ?= ska-tmc-common ## list of charts
K8S_CHART ?= $(HELM_CHART)

CI_REGISTRY ?= gitlab.com
CUSTOM_VALUES = --set test_device.image.tag=$(VERSION)
K8S_TEST_IMAGE_TO_TEST=$(CAR_OCI_REGISTRY_HOST)/$(PROJECT):$(VERSION)
ifneq ($(CI_JOB_ID),)
CUSTOM_VALUES = --set test_device.image.image=$(PROJECT) \
	--set test_device.image.registry=$(CI_REGISTRY)/ska-telescope/ska-tmc/$(PROJECT) \
	--set test_device.image.tag=$(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA)
K8S_TEST_IMAGE_TO_TEST=$(CI_REGISTRY)/ska-telescope/ska-tmc/$(PROJECT)/$(PROJECT):$(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA)
endif

CI_PROJECT_DIR ?= .

XAUTHORITY ?= $(HOME)/.Xauthority
THIS_HOST := $(shell ip a 2> /dev/null | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' | head -n1)
DISPLAY ?= $(THIS_HOST):0
JIVE ?= false# Enable jive
MINIKUBE ?= false ## Minikube or not

# Test runner - run to completion job in K8s
# name of the pod running the k8s_tests
K8S_TEST_RUNNER = test-runner-$(HELM_RELEASE)
ADDMARK ?= #additional markers
# override for python-test - must not have the above --true-context
ifeq ($(MAKECMDGOALS),python-test)
ADD_ARGS += --forked
MARK = not post_deployment and not acceptance $(ADDMARK)
endif
ifeq ($(MAKECMDGOALS),k8s-test)
ADD_ARGS +=  --true-context
MARK = (post_deployment or acceptance) $(ADDMARK)
endif

ifeq ($(EXIT_AT_FAIL),true)
ADD_ARGS += -x
endif

PYTHON_VARS_AFTER_PYTEST ?= -m '$(MARK)' $(ADD_ARGS) $(FILE)

K8S_CHART_PARAMS = --set global.minikube=$(MINIKUBE) \
	--set global.tango_host=$(TANGO_HOST) \
	--set ska-tango-base.display=$(DISPLAY) \
	--set ska-tango-base.xauthority=$(XAUTHORITY) \
	--set ska-tango-base.jive.enabled=$(JIVE) \
	--set telescope=$(TELESCOPE) \
	--set global.exposeAllDS=false \
	--set global.cluster_domain=$(CLUSTER_DOMAIN) \
	--set global.operator=$(SKA_TANGO_OPERATOR) \
	$(CUSTOM_VALUES)

K8S_TEST_TEST_COMMAND = $(PYTHON_VARS_BEFORE_PYTEST) $(PYTHON_RUNNER) \
						pytest \
						$(PYTHON_VARS_AFTER_PYTEST) ./tests \
						| tee pytest.stdout


PYTHON_BUILD_TYPE = non_tag_setup

-include .make/base.mk
-include .make/python.mk
-include PrivateRules.mak
-include .make/oci.mk
-include .make/k8s.mk
-include .make/helm.mk

# Issue resolution with twine during publish
python-pre-publish:
	pip3 install twine

test-requirements:
	@poetry export --without-hashes --with dev --format requirements.txt --output tests/requirements.txt

k8s-pre-test: python-pre-test test-requirements

requirements: ## Install Dependencies
	poetry install


# .PHONY is additive
.PHONY: unit-test


