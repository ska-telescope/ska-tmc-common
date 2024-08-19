import time

import pytest

from ska_tmc_common import DeviceInfo, InputParameter, TmcComponentManager
from tests.settings import logger
from tests.test_component import TestTMCComponent


@pytest.mark.ska_mid
@pytest.mark.post_deployment
def test_new_component():
    cm = TmcComponentManager(
        _component=TestTMCComponent(logger=logger),
        _input_parameter=InputParameter(None),
        logger=logger,
    )
    dev_info = DeviceInfo("mid-csp/subarray/01", True)  # exported device
    cm._component.update_device(dev_info)
    lp = cm.liveliness_probe_object
    lp.add_device("mid-csp/subarray/01")
    time.sleep(2)
    assert not cm._component.get_device("mid-csp/subarray/01")._unresponsive

    dev_info = DeviceInfo("low-csp/subarray/01", True)  # exported device
    cm._component.update_device(dev_info)
    lp = cm.liveliness_probe_object
    lp.add_device("low-csp/subarray/01")
    time.sleep(2)
    assert cm._component.get_device("low-csp/subarray/01")._unresponsive
    assert (
        "Unable to reach device low-csp/subarray/01"
        == cm._component.get_device("low-csp/subarray/01").exception
    )
