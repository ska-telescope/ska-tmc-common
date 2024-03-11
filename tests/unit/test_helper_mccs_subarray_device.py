import json

import pytest
import tango
from ska_tango_base.commands import ResultCode
from ska_tango_testing.mock.placeholders import Anything

from ska_tmc_common import DevFactory, FaultType
from tests.settings import MCCS_SUBARRAY_DEVICE


@pytest.mark.aki
def test_lrcr_event(tango_context, group_callback):
    mccs_subarray = DevFactory().get_device(MCCS_SUBARRAY_DEVICE)
    mccs_subarray.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        group_callback["longRunningCommandResult"],
    )
    defective_params = json.dumps(
        {
            "enabled": True,
            "fault_type": FaultType.LONG_RUNNING_EXCEPTION,
            "error_message": "Default exception.",
            "result": ResultCode.FAILED,
        }
    )
    mccs_subarray.SetDefective(defective_params)
    _, _ = mccs_subarray.Configure("")
    while True:
        assertion_data = group_callback[
            "longRunningCommandResult"
        ].assert_change_event(
            (Anything, Anything),
        )
        if assertion_data:
            if assertion_data["attribute_value"][1] == json.dumps(
                [ResultCode.FAILED, "Default exception."]
            ):
                break
