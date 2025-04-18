"""
This module contains the fixtures, methods and devices required for testing.
A module defining a list of fixtures that are shared across all ska_tmc_common
tests.

"""

# pylint: disable=unused-argument
import logging
import time
import types
from os.path import dirname, join

import pytest
import tango
from ska_control_model import ObsState
from ska_tango_testing.mock import MockCallable
from ska_tango_testing.mock.tango.event_callback import (
    MockTangoEventCallbackGroup,
)
from tango.test_context import DeviceTestContext, MultiDeviceTestContext

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
    HelperMccsSubarrayDevice,
    HelperSDPMasterLeafNode,
    HelperSdpQueueConnector,
    HelperSdpSubarray,
    HelperSdpSubarrayLeafDevice,
    HelperSubArrayDevice,
    TmcLeafNodeComponentManager,
)
from ska_tmc_common.v1.tmc_base_leaf_device import TMCBaseLeafDevice
from ska_tmc_common.v1.tmc_component_manager import (
    TmcLeafNodeComponentManager as CmV1,
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
    HELPER_SDP_MASTER_LEAF_DEVICE,
    HELPER_SDP_QUEUE_CONNECTOR_DEVICE,
    MCCS_SUBARRAY_DEVICE,
    SDP_LEAF_NODE_DEVICE,
    SDP_SUBARRAY_DEVICE_LOW,
    SDP_SUBARRAY_DEVICE_MID,
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
    :return: devices to load list
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
            "class": TMCBaseLeafDevice,
            "devices": [{"name": DEVICE_LIST[3]}],
        },
        {
            "class": HelperBaseDevice,
            "devices": [{"name": DEVICE_LIST[1]}, {"name": DEVICE_LIST[2]}],
        },
        {
            "class": HelperSubArrayDevice,
            "devices": [
                {"name": SUBARRAY_DEVICE},
            ],
        },
        {
            "class": HelperMccsSubarrayDevice,
            "devices": [
                {"name": MCCS_SUBARRAY_DEVICE},
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
                {
                    "name": DISH_LN_DEVICE,
                    "properties": {
                        "DishMasterFQDN": "ska001/elt/master",
                    },
                },
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
            "class": HelperSDPMasterLeafNode,
            "devices": [
                {"name": HELPER_SDP_MASTER_LEAF_DEVICE},
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
            "class": HelperSdpQueueConnector,
            "devices": [
                {"name": HELPER_SDP_QUEUE_CONNECTOR_DEVICE},
            ],
        },
    )


@pytest.fixture
def tango_context(devices_to_load, request):
    """
    It provides the tango context to invoke any command.
    :yields: device_context
    """
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with MultiDeviceTestContext(
            devices_to_load, process=False, timeout=50
        ) as context:
            DevFactory._test_context = context
            logging.info("test context set")
            yield context
    else:
        yield None


@pytest.fixture
def group_callback() -> MockTangoEventCallbackGroup:
    """
    Creates a mock callback group for asynchronous testing
    :return: group callback
    :rtype: MockTangoEventCallbackGroup
    """
    group_callback = MockTangoEventCallbackGroup(
        "longRunningCommandResult",
        timeout=50,
    )
    return group_callback


@pytest.fixture(params=[TmcLeafNodeComponentManager, CmV1])
def component_manager(request):
    """
    Create a component manager instance for a dummy device for testing.

    :return: Component manager
    :rtype: TmcLeafNodeComponentManager
    """
    dummy_device = DeviceInfo("dummy/monitored/device")
    cm_cls = request.param
    cm = cm_cls(logger)
    cm._device = dummy_device

    def update_device_obs_state(self, obs_state: ObsState) -> None:
        """
        Update a monitored device obs state,
        and call the relative callbacks if available
        :param obs_state: obs state of the device
        :type obs_state: ObsState
        """

        dev_info = self.get_device()
        dev_info.obs_state = obs_state
        dev_info.last_event_arrived = time.time()

    cm.update_device_obs_state = types.MethodType(update_device_obs_state, cm)
    return cm


@pytest.fixture(params=[TmcLeafNodeComponentManager])
def component_manager_old(request):
    """
    Create a component manager instance for a dummy device for testing.

    :return: Component manager
    :rtype: TmcLeafNodeComponentManager
    """
    dummy_device = DeviceInfo("dummy/monitored/device")
    cm_cls = request.param
    cm = cm_cls(logger)
    cm._device = dummy_device

    return cm


@pytest.fixture
def task_callback() -> MockCallable:
    """
    Creates a mock callable for asynchronous testing
    :return: task callback
    :rtype: MockCallable
    """
    task_callback = MockCallable(15)
    return task_callback


@pytest.fixture
def csp_sln_dev_name() -> str:
    """
    Fixture for returning csp subarray FQDN
    :return: FQDN
    rtype: str
    """
    # testing device
    return "ska_mid/tm_leaf_node/csp_subarray01"


def get_input_str(path) -> str:
    """
    Returns input json string
    :return: json string
    :rtype: str
    """
    with open(path, "r", encoding="utf-8") as f:
        input_str = f.read()
    return input_str


@pytest.fixture()
def json_factory():
    """
    Json factory for getting json files
    :return: json factory
    """

    def _get_json(slug):
        return get_input_str(join(dirname(__file__), "data", f"{slug}.json"))

    return _get_json


@pytest.fixture
def sdp_subarray_low(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(
            HelperSdpSubarray,
            device_name=SDP_SUBARRAY_DEVICE_LOW,
            timeout=20,
        ) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class(
            "HelperSdpSubarray"
        )
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


@pytest.fixture
def sdp_subarray_mid(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(
            HelperSdpSubarray,
            device_name=SDP_SUBARRAY_DEVICE_MID,
            timeout=20,
        ) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class(
            "HelperSdpSubarray"
        )
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break
