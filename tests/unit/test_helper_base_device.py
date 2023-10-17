from ska_tmc_common import DevFactory
from tests.settings import CSP_LEAF_NODE_DEVICE, SDP_LEAF_NODE_DEVICE


def test_set_raise_exception_csp(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(CSP_LEAF_NODE_DEVICE)
    assert not subarray_device.raiseException
    subarray_device.SetRaiseException(True)
    assert subarray_device.raiseException


def test_set_raise_exception_sdp(tango_context):
    dev_factory = DevFactory()
    subarray_device = dev_factory.get_device(SDP_LEAF_NODE_DEVICE)
    assert not subarray_device.raiseException
    subarray_device.SetRaiseException(True)
    assert subarray_device.raiseException
