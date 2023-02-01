import pytest
from ska_tango_base.commands import ResultCode

from tests.conftest import tear_down


@pytest.mark.temp
def test_command_execution(helper_device, group_callback, caplog):
    # os.environ["TANGO_HOST"] = "tango-databaseds:10000"
    # helper_device.subscribe_event(
    #     "healthState",
    #     tango.EventType.CHANGE_EVENT,
    #     group_callback["healthState"],
    #     stateless=True,
    # )
    result, _ = helper_device.On()
    assert result[0] == ResultCode.OK
    tear_down(helper_device)
    # caplog.set_level(logging.DEBUG, logger="ska_tango_testing.mock")
    # group_callback["healthState"].assert_change_event(
    #     HealthState.OK,
    #     lookahead=1,
    # )
    # assert helper_device.StopTimer


# @pytest.mark.temp
# def test_command_timeout(helper_device, group_callback, caplog):
#     os.environ["TANGO_HOST"] = "tango-databaseds:10000"
#     # helper_device.subscribe_event(
#     #     "healthState",
#     #     tango.EventType.CHANGE_EVENT,
#     #     group_callback["healthState"],
#     #     stateless=True,
#     # )
#     helper_device.SleepTime = 10
#     with pytest.raises(TimeoutOccured):
#         helper_device.On()
# caplog.set_level(logging.DEBUG, logger="ska_tango_testing.mock")
# group_callback["healthState"].assert_change_event(
#     HealthState.OK,
#     lookahead=1,
# )
