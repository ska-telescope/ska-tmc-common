import logging
import time

import pytest

from ska_tmc_common import (
    DummyTmcDevice,
    HelperStateDevice,
    InputParameter,
    TmcComponentManager,
)

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
    for dev_info in cm.checked_devices:
        if dev_info.unresponsive:
            result += 1
    return result


def create_cm(
    _input_parameter=InputParameter(None),
    p_liveliness_probe=True,
    p_event_receiver=True,
):
    cm = TmcComponentManager(
        _input_parameter=_input_parameter,
        logger=logger,
        _liveliness_probe=p_liveliness_probe,
        _event_receiver=p_event_receiver,
    )

    start_time = time.time()
    return cm, start_time


def set_devices_state(devices, state, devFactory, cm, expected_elapsed_time):
    for device in devices:
        proxy = devFactory.get_device(device)
        proxy.SetDirectState(state)
        assert proxy.State() == state


def set_device_state(device, state, devFactory):
    proxy = devFactory.get_device(device)
    proxy.SetDirectState(state)
    assert proxy.State() == state
