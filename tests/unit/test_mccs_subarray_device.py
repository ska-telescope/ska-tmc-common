import json

import pytest
from ska_tango_base.commands import ResultCode

from ska_tmc_common import DevFactory
from ska_tmc_common.test_helpers.helper_mccs_subarray import HelperMccsSubarray
from tests.settings import MCCS_SUBARRAY_DEVICE


@pytest.fixture(scope="module")
def devices_to_load():
    return (
        {
            "class": HelperMccsSubarray,
            "devices": [{"name": MCCS_SUBARRAY_DEVICE}],
        },
    )


@pytest.mark.mccs
def test_set_delay(tango_context):
    dev_factory = DevFactory()
    mccs_subarray_device = dev_factory.get_device(MCCS_SUBARRAY_DEVICE)
    mccs_subarray_device.SetDelay('{"Configure": 3}')
    command_delay_info = json.loads(mccs_subarray_device.commandDelayInfo)
    assert command_delay_info["Configure"] == 3


def test_set_defective(tango_context):
    dev_factory = DevFactory()
    mccs_subarray_device = dev_factory.get_device(MCCS_SUBARRAY_DEVICE)
    mccs_subarray_device.SetDefective(json.dumps({"enabled": True}))
    result, message = mccs_subarray_device.AssignResources("")
    assert result[0] == ResultCode.FAILED
    assert message[0] == "Default exception."
    mccs_subarray_device.SetDefective(json.dumps({"enabled": False}))


def test_assignresources_attribute(tango_context):
    """Test assignResources attribute"""
    dev_factory = DevFactory()
    mccs_subarray_device = dev_factory.get_device(MCCS_SUBARRAY_DEVICE)
    mccs_subarray_device.assignedResources = '{"beam_id: 1}'
    assert mccs_subarray_device.assignedResources == '{"beam_id: 1}'
