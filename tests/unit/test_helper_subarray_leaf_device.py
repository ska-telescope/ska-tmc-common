from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from tests.settings import SUBARRAY_LEAF_DEVICE


def test_assign_resources(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SUBARRAY_LEAF_DEVICE)
    result, message = subarray_leaf_device.AssignResources("")
    assert result[0] == ResultCode.OK
    assert message[0] == ""


def test_assign_resources_defective(tango_context):
    dev_factory = DevFactory()
    subarray_leaf_device = dev_factory.get_device(SUBARRAY_LEAF_DEVICE)
    subarray_leaf_device.SetDefective(True)
    result, message = subarray_leaf_device.AssignResources("")
    assert result[0] == ResultCode.QUEUED
    assert message[0] == ""
