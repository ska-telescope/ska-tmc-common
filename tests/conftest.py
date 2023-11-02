"""
This module contains the fixtures, methods and devices required for testing.
A module defining a list of fixtures that are shared across all ska_tmc_common
tests.

"""

# pylint: disable=unused-argument
import logging
from os.path import dirname, join

import pytest
import tango
from ska_tango_testing.mock import MockCallable
from tango.test_context import MultiDeviceTestContext

from ska_tmc_common import (
    DevFactory,
    DeviceInfo,
    DummyTmcDevice,
    HelperBaseDevice,
    HelperCspMasterDevice,
    HelperCspMasterLeafDevice,
    HelperCspSubarrayLeafDevice,
    HelperDishDevice,
    HelperDishLNDevice,
    HelperMCCSController,
    HelperMCCSMasterLeafNode,
    HelperMccsSubarrayLeafNode,
    HelperSdpSubarrayLeafDevice,
    HelperSubArrayDevice,
    TmcLeafNodeComponentManager,
)
from tests.settings import (
    CSP_DEVICE,
    CSP_LEAF_NODE_DEVICE,
    DEVICE_LIST,
    DISH_DEVICE,
    DISH_LN_DEVICE,
    HELPER_CSP_MASTER_LEAF_DEVICE,
    HELPER_MCCS_CONTROLLER,
    HELPER_MCCS_MASTER_LEAF_NODE_DEVICE,
    HELPER_MCCS_SUBARRAY_DEVICE,
    HELPER_MCCS_SUBARRAY_LEAF_NODE_DEVICE,
    SDP_LEAF_NODE_DEVICE,
    SUBARRAY_DEVICE,
    TMC_COMMON_DEVICE,
    logger,
)


def pytest_sessionstart(session):
    """
    Pytest hook; prints info about tango version.
    :param session: a pytest Session object
    :type session: class:`pytest.Session`
    """
    print(tango.utils.info())


def pytest_addoption(parser):
    """
    Pytest hook; implemented to add the `--true-context` option, used to
    indicate that a true Tango subsystem is available, so there is no
    need for a class:`tango.test_context.MultiDeviceTestContext`.
    :param parser: the command line options parser
    :type parser: class:`argparse.ArgumentParser`
    """
    parser.addoption(
        "--true-context",
        action="store_true",
        default=False,
        help=(
            "Tell pytest that you have a true Tango context and don't "
            "need to spin up a Tango test context"
        ),
    )


@pytest.fixture(scope="module")
def devices_to_load():
    """
    This method contains the list of devices to load.
    """
    return (
        {
            "class": DummyTmcDevice,
            "devices": [
                {"name": TMC_COMMON_DEVICE},
                {"name": DEVICE_LIST[0]},
            ],
        },
        {
            "class": HelperBaseDevice,
            "devices": [{"name": DEVICE_LIST[1]}, {"name": DEVICE_LIST[2]}],
        },
        {
            "class": HelperSubArrayDevice,
            "devices": [
                {"name": SUBARRAY_DEVICE},
                {"name": HELPER_MCCS_SUBARRAY_DEVICE},
            ],
        },
        {
            "class": HelperDishDevice,
            "devices": [
                {"name": DISH_DEVICE},
            ],
        },
        {
            "class": HelperDishLNDevice,
            "devices": [
                {"name": DISH_LN_DEVICE},
            ],
        },
        {
            "class": HelperCspMasterDevice,
            "devices": [
                {"name": CSP_DEVICE},
            ],
        },
        {
            "class": HelperCspMasterLeafDevice,
            "devices": [
                {"name": HELPER_CSP_MASTER_LEAF_DEVICE},
            ],
        },
        {
            "class": HelperCspSubarrayLeafDevice,
            "devices": [
                {"name": CSP_LEAF_NODE_DEVICE},
            ],
        },
        {
            "class": HelperSdpSubarrayLeafDevice,
            "devices": [
                {"name": SDP_LEAF_NODE_DEVICE},
            ],
        },
        {
            "class": HelperMCCSMasterLeafNode,
            "devices": [
                {"name": HELPER_MCCS_MASTER_LEAF_NODE_DEVICE},
            ],
        },
        {
            "class": HelperMCCSController,
            "devices": [
                {"name": HELPER_MCCS_CONTROLLER},
            ],
        },
        {
            "class": HelperMccsSubarrayLeafNode,
            "devices": [
                {"name": HELPER_MCCS_SUBARRAY_LEAF_NODE_DEVICE},
            ],
        },
    )


@pytest.fixture(scope="module")
def tango_context(devices_to_load, request):
    """
    It provides the tango context to invoke any command.
    """
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with MultiDeviceTestContext(devices_to_load, process=False) as context:
            DevFactory._test_context = context
            logging.info("test context set")
            yield context
    else:
        yield None


@pytest.fixture
def component_manager() -> TmcLeafNodeComponentManager:
    """create a component manager instance for dummy device for testing

    git :rtype : TmcLeafNodeComponentManager
    """
    dummy_device = DeviceInfo("dummy/monitored/device")
    cm = TmcLeafNodeComponentManager(logger)
    cm._device = dummy_device
    return cm


@pytest.fixture
def task_callback() -> MockCallable:
    """Creates a mock callable for asynchronous testing

    :rtype: MockCallable
    """
    task_callback = MockCallable(15)
    return task_callback


@pytest.fixture
def csp_sln_dev_name() -> str:
    """
    Fixture for returning csp subarray FQDN
    rtype: str
    """
    # testing device
    return "ska_mid/tm_leaf_node/csp_subarray01"


def get_input_str(path) -> str:
    """
    Returns input json string
    :rtype: String
    """
    with open(path, "r", encoding="utf-8") as f:
        input_str = f.read()
    return input_str


@pytest.fixture()
def json_factory():
    """
    Json factory for getting json files
    """

    def _get_json(slug):
        return get_input_str(join(dirname(__file__), "data", f"{slug}.json"))

    return _get_json
