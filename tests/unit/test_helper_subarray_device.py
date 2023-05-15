import time

from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import SUBARRAY_DEVICE


def test_set_delay(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    assert subarray_device.delay == 2
    subarray_device.SetDelay(5)
    assert subarray_device.delay == 5


def test_set_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    assert not subarray_device.defective
    subarray_device.SetDefective(True)
    assert subarray_device.defective


def test_assign_resources(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    result, message = subarray_device.AssignResources("")
    assert result[0] == ResultCode.OK
    assert message[0] == ""
    assert subarray_device.obsstate == ObsState.RESOURCING
    time.sleep(2.5)
    assert subarray_device.obsstate == ObsState.IDLE


def test_assign_resources_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.SetDefective(True)
    result, message = subarray_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert (
        message[0] == "Device is Defective, cannot process command completely."
    )
    assert subarray_device.obsstate == ObsState.RESOURCING
