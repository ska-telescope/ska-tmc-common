from unittest.mock import Mock

from tango.test_context import DeviceTestContext

from ska_tmc_common import HelperBaseDevice
from ska_tmc_common.v2.event_manager import EventManager

DUMMY_CONFIG = {"device1": ["attribute1"]}
DUMMY_SUBSCRIPTION_CONFIG = {"device": {"attribute1": {"subscritption_id": 1}}}
TIMER_THREAD_NAME = "timer_thread_1"
DEVICE_NAME = "a/a/1"
ATTRIBTUE_NAME = "attribute1"
TANGO_HOST = "tango_host.namespace.svc.cluster.local:1000"
ATTRIBUTE_FQDN = f"tango://{TANGO_HOST}/{DEVICE_NAME}/{ATTRIBTUE_NAME}"


def test_event_manager():
    event_manager = EventManager(Mock())
    assert event_manager.subscription_configruation is None
    assert event_manager.pending_configuration == {}
    event_manager.pending_configuration = DUMMY_CONFIG
    assert event_manager.pending_configuration == DUMMY_CONFIG
    assert event_manager.stateless_flag
    event_manager.stateless_flag = False
    assert not event_manager.stateless_flag
    assert event_manager.device_subscriptions == {}
    event_manager.device_subscriptions = DUMMY_SUBSCRIPTION_CONFIG
    assert event_manager.device_subscriptions == DUMMY_SUBSCRIPTION_CONFIG
    assert event_manager.device_errors_tracker == {}
    event_manager.init_timeout(12)
    assert not event_manager._EventManager__thread_time_outs.get(12)
    event_manager.set_timeout(12)
    assert event_manager._EventManager__thread_time_outs.get(12)
    event_manager.start_timer(TIMER_THREAD_NAME, 1)
    assert event_manager._EventManager__timer_threads.get(TIMER_THREAD_NAME)
    event_manager.stop_timer(TIMER_THREAD_NAME)
    assert not event_manager._EventManager__timer_threads.get(
        TIMER_THREAD_NAME
    )
    event_manager.device_subscriptions = {}
    event_manager.init_device_subscriptions("device")
    assert event_manager.device_subscriptions.get("device") == {}
    event_manager.update_device_subscriptions("device", "attribute1", 1)
    assert event_manager.device_subscriptions.get("device") == {
        "attribute1": {"subscription_id": 1}
    }
    event_manager.update_device_subscriptions(
        "device", is_subscription_completed=True
    )
    assert event_manager.device_subscriptions.get("device").get(
        "is_subscription_completed"
    )

    with DeviceTestContext(
        HelperBaseDevice, device_name=DEVICE_NAME, timeout=50
    ):
        proxy = event_manager.get_device_proxy(DEVICE_NAME)
        assert proxy.ping() > -1
    DUMMY_SUBSCRIPTION_CONFIG_COPY = DUMMY_SUBSCRIPTION_CONFIG.copy()
    event_manager.remove_subscribed_devices(
        DUMMY_SUBSCRIPTION_CONFIG_COPY,
    )
    assert not DUMMY_SUBSCRIPTION_CONFIG_COPY.get("device")
    device_name, attribute_name = event_manager.get_device_and_attribute_name(
        ATTRIBUTE_FQDN
    )
    assert device_name == DEVICE_NAME
    assert attribute_name == ATTRIBTUE_NAME
