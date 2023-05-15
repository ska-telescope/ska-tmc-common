import time

from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import SUBARRAY_DEVICE


def test_set_defective(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    assert not subarray_device.defective
    subarray_device.SetDefective(True)
    assert subarray_device.defective


def test_restart_command(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SUBARRAY_DEVICE)
    subarray_device.SetDirectObsState(ObsState.ABORTED)
    assert subarray_device.obsstate == ObsState.ABORTED
    result, message = subarray_device.Restart()
    assert result[0] == ResultCode.OK
    assert message[0] == ""
    assert subarray_device.obsstate == ObsState.RESTARTING
    time.sleep(3)
    assert subarray_device.obsstate == ObsState.EMPTY
