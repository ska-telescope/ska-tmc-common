from unittest.mock import Mock

from ska_tmc_common.v2.event_manager import EventManager

DUMMY_CONFIG = {"device1": ["attribute1"]}
DUMMY_SUBSCRIPTION_CONFIG = {"device": {"attribute1": {"subscritption_id": 1}}}


def test_init_event_manager():
    event_manager = EventManager(Mock())
    assert event_manager.subscription_configruation is None
    assert event_manager.pending_configuration == {}
    event_manager.pending_configuration = DUMMY_CONFIG
    assert event_manager.pending_configuration == DUMMY_CONFIG
    assert event_manager.stateless_flag
    event_manager.stateless_flag = False
    assert not event_manager.stateless_flag
    assert event_manager.device_subscription_configuration == {}
    event_manager.device_subscription_configuration = DUMMY_SUBSCRIPTION_CONFIG
    assert (
        event_manager.device_subscription_configuration
        == DUMMY_SUBSCRIPTION_CONFIG
    )
    assert event_manager.device_error_tracking == {}
