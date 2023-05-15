"""
This module contains the fixtures, methods and variables required for testing.
"""

import logging
import time
from typing import Tuple

import pytest
import tango

from ska_tmc_common import (
    DevFactory,
    DummyTmcDevice,
    HelperBaseDevice,
    InputParameter,
    LivelinessProbeType,
    TmcComponentManager,
)

logger = logging.getLogger(__name__)

SLEEP_TIME = 0.5
TIMEOUT = 10

DishLeafNodePrefix = "ska_mid/tm_leaf_node/d0"
NumDishes = 10

DEVICE_LIST = ["dummy/tmc/device", "test/device/1", "test/device/2"]


@pytest.fixture(scope="module")
def devices_to_load():
    """
    This method contains the list of devices to load.
    """
    return (
        {
            "class": DummyTmcDevice,
            "devices": [{"name": "dummy/tmc/device"}],
        },
        {
            "class": HelperBaseDevice,
            "devices": [{"name": "test/device/1"}, {"name": "test/device/2"}],
        },
    )


def count_faulty_devices(cm):
    """
    It counts the number of faulty devices present.
    """
    result = 0
    for dev_info in cm.checked_devices:
        if dev_info.unresponsive:
            result += 1
    return result


def create_cm(
    _input_parameter: InputParameter = InputParameter(None),
    p_liveliness_probe: LivelinessProbeType = LivelinessProbeType.MULTI_DEVICE,
    p_event_receiver: bool = True,
) -> Tuple[TmcComponentManager, float]:
    """
    It creates the instance of the component manager class.
    """
    cm = TmcComponentManager(
        _input_parameter=_input_parameter,
        logger=logger,
        _liveliness_probe=p_liveliness_probe,
        _event_receiver=p_event_receiver,
    )

    start_time = time.time()
    return cm, start_time


def set_devices_state(
    devices: list, state: tango.DevState, devFactory: DevFactory
) -> None:
    """
    It sets the state of multiple devices
    """
    for device in devices:
        proxy = devFactory.get_device(device)
        proxy.SetDirectState(state)
        assert proxy.State() == state


def set_device_state(
    device: str, state: tango.DevState, devFactory: DevFactory
) -> None:
    """
    It sets the state of the device
    """
    proxy = devFactory.get_device(device)
    proxy.SetDirectState(state)
    assert proxy.State() == state
