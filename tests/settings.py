import logging
import time

import pytest

from ska_tmc_common.op_state_model import TMCOpStateModel
from ska_tmc_common.tmc_component_manager import TmcComponentManager
from tests.helpers.helper_state_device import HelperStateDevice
from tests.helpers.helper_tmc_device import DummyTmcDevice

logger = logging.getLogger(__name__)

SLEEP_TIME = 0.5
TIMEOUT = 10

DishLeafNodePrefix = "ska_mid/tm_leaf_node/d"
NumDishes = 10

DEVICE_LIST = ["dummy/tmc/device", "test/device/1", "test/device/2"]


@pytest.fixture(scope="module")
def devices_to_load():
    return (
        {
            "class": DummyTmcDevice,
            "devices": [{"name": "dummy/tmc/device"}],
        },
        {
            "class": HelperStateDevice,
            "devices": [{"name": "test/device/1"}, {"name": "test/device/2"}],
        },
    )


def count_faulty_devices(cm):
    result = 0
    for devInfo in cm.checked_devices:
        if devInfo.unresponsive:
            result += 1
    return result


def create_cm(p_monitoring_loop=True, p_event_receiver=True):
    op_state_model = TMCOpStateModel(logger)
    cm = TmcComponentManager(
        op_state_model,
        logger=logger,
        _monitoring_loop=p_monitoring_loop,
        _event_receiver=p_event_receiver,
    )

    # for dev in DEVICE_LIST:
    #     cm.add_device(dev)
    start_time = time.time()
    # num_devices = len(DEVICE_LIST)
    # if not p_monitoring_loop:
    #     return cm, start_time
    # while num_devices != len(cm.checked_devices):
    #     time.sleep(SLEEP_TIME)
    #     elapsed_time = time.time() - start_time
    #     if elapsed_time > TIMEOUT:
    #         pytest.fail("Timeout occurred while executing the test")

    return cm, start_time


# def create_cm_no_faulty_devices(
#     tango_context,
#     p_monitoring_loop,
#     p_event_receiver
# ):
#     logger.info("%s", tango_context)

#     cm, start_time = create_cm(
#         p_monitoring_loop, p_event_receiver )
#     num_faulty = count_faulty_devices(cm)
#     assert num_faulty == 0
#     elapsed_time = time.time() - start_time
#     logger.info("checked %s devices in %s", num_faulty, elapsed_time)
#     return cm


# def ensure_telescope_state(cm, state, expected_elapsed_time):
#     start_time = time.time()
#     elapsed_time = 0
#     while cm.component.telescope_state != state:
#         elapsed_time = time.time() - start_time
#         time.sleep(0.1)
#         if elapsed_time > TIMEOUT:
#             pytest.fail("Timeout occurred while executing the test")
#     assert elapsed_time < expected_elapsed_time


# def ensure_tmc_op_state(cm, state, expected_elapsed_time):
#     start_time = time.time()
#     elapsed_time = 0
#     while cm.component.tmc_op_state != state:
#         elapsed_time = time.time() - start_time
#         time.sleep(0.1)
#         if elapsed_time > TIMEOUT:
#             pytest.fail("Timeout occurred while executing the test")
#     assert elapsed_time < expected_elapsed_time


# def ensure_imaging(cm, value, expected_elapsed_time):
#     start_time = time.time()
#     elapsed_time = 0
#     while cm.component.imaging != value:
#         elapsed_time = time.time() - start_time
#         time.sleep(0.1)
#         if elapsed_time > TIMEOUT:
#             pytest.fail("Timeout occurred while executing the test")
#     assert elapsed_time < expected_elapsed_time


def set_devices_state(devices, state, devFactory, cm, expected_elapsed_time):
    for device in devices:
        proxy = devFactory.get_device(device)
        proxy.SetDirectState(state)
        assert proxy.State() == state


def set_device_state(device, state, devFactory):
    proxy = devFactory.get_device(device)
    proxy.SetDirectState(state)
    assert proxy.State() == state
