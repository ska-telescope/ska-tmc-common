import os
import time

import pytest
import tango

from ska_tmc_common import DeviceInfo, InputParameter
from ska_tmc_common.v1.tmc_component_manager import TmcComponentManager
from tests.settings import (
    CSP_SUBARRAY_DEVICE,
    SDP_SUBARRAY_DEVICE,
    SUBARRAY_LEAF_DEVICE,
    export_device,
    logger,
)
from tests.test_component import TestTMCComponent

TANGO_HOST = os.getenv("TANGO_HOST")


@pytest.mark.post_deployment
def test_liveliness_probe():
    cm = TmcComponentManager(
        _component=TestTMCComponent(logger=logger),
        _input_parameter=InputParameter(None),
        logger=logger,
    )
    dev_info = DeviceInfo(CSP_SUBARRAY_DEVICE, True)  # exported device
    cm._component.update_device(dev_info)
    lp = cm.liveliness_probe_object
    lp.add_device(CSP_SUBARRAY_DEVICE)
    time.sleep(4)
    assert not cm._component.get_device(CSP_SUBARRAY_DEVICE).unresponsive

    # full_trl
    full_trl = "tango://" + TANGO_HOST + "/" + SUBARRAY_LEAF_DEVICE
    dev_info = DeviceInfo(full_trl, True)
    cm._component.update_device(dev_info)
    lp = cm.liveliness_probe_object
    lp.add_device(full_trl)
    time.sleep(2)
    assert not cm._component.get_device(full_trl).unresponsive

    # device not in the database
    full_trl = "tango://" + TANGO_HOST + "/" + SDP_SUBARRAY_DEVICE
    dev_info = DeviceInfo(full_trl, False)
    cm._component.update_device(dev_info)
    lp = cm.liveliness_probe_object
    lp.add_device(full_trl)
    time.sleep(2)
    assert cm._component.get_device(full_trl).unresponsive
    assert (
        f"Unable to reach device {full_trl}"
        == cm._component.get_device(full_trl).exception
    )

    # check unexported
    db = tango.Database()
    db_device_info = db.get_device_info(CSP_SUBARRAY_DEVICE)
    db.unexport_device(CSP_SUBARRAY_DEVICE)
    time.sleep(2)
    assert cm._component.get_device(CSP_SUBARRAY_DEVICE).unresponsive
    assert (
        f"Device is not yet exported: {CSP_SUBARRAY_DEVICE}"
        == cm._component.get_device(CSP_SUBARRAY_DEVICE).exception
    )

    # exported device again
    export_device(db, db_device_info)
    time.sleep(2)
    assert not cm._component.get_device(CSP_SUBARRAY_DEVICE).unresponsive
    assert "" == cm._component.get_device(CSP_SUBARRAY_DEVICE).exception
