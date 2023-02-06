import os

import pytest
import tango
from ska_tango_base.commands import ResultCode

from ska_tmc_common.enum import Timeout
from tests.conftest import tear_down


@pytest.mark.skip(reason="Will fail as a unit test")
def test_command_execution(group_callback):
    os.environ["TANGO_HOST"] = "localhost:10000"
    proxy = tango.DeviceProxy("helper/state/device")
    event_id = proxy.subscribe_event(
        "State",
        tango.EventType.CHANGE_EVENT,
        group_callback["State"],
    )
    result, _ = proxy.On()
    assert result[0] == ResultCode.OK

    group_callback["State"].assert_change_event(
        tango._tango.DevState.ON,
        lookahead=3,
    )
    tear_down(proxy, [event_id])


@pytest.mark.skip(reason="Will fail as a unit test")
def test_command_timeout(group_callback):
    os.environ["TANGO_HOST"] = "localhost:10000"
    proxy = tango.DeviceProxy("helper/state/device")
    event_id = proxy.subscribe_event(
        "State",
        tango.EventType.CHANGE_EVENT,
        group_callback["State"],
    )
    event_id2 = proxy.subscribe_event(
        "Timeout",
        tango.EventType.CHANGE_EVENT,
        group_callback["Timeout"],
    )
    # with pytest.raises(TimeoutOccured):
    result, _ = proxy.On()
    assert result[0] == ResultCode.OK

    group_callback["Timeout"].assert_change_event(Timeout.OCCURED, lookahead=2)

    tear_down(proxy, [event_id, event_id2])
