# Standard Python imports

import mock
from mock import Mock

# Additional imports
from src.ska_tmc_common.tango_server_helper import TangoServerHelper


def test_set_status():
    with mock.patch.object(
        TangoServerHelper, "get_instance", return_value=Mock()
    ):
        device_proxy = TangoServerHelper.get_instance()
        device_proxy.Status = "Testing status for mock device"
        device_proxy.set_status("Testing status for mock device")
        device_proxy.set_status.assert_called_with(
            "Testing status for mock device"
        )


def test_get_status():
    with mock.patch.object(
        TangoServerHelper, "get_instance", return_value=Mock()
    ):
        device_proxy = TangoServerHelper.get_instance()
        device_proxy.get_status()
        device_proxy.get_status.assert_called_with()


def test_read_property():
    with mock.patch.object(
        TangoServerHelper, "get_instance", return_value=Mock()
    ):
        device_proxy = TangoServerHelper.get_instance()
        device_proxy.read_property("CentralAlarmHandler")
        device_proxy.read_property.assert_called_with("CentralAlarmHandler")


def test_write_property():
    with mock.patch.object(
        TangoServerHelper, "get_instance", return_value=Mock()
    ):
        device_proxy = TangoServerHelper.get_instance()
        device_proxy.write_property("skalevel", 1)
        device_proxy.write_property.assert_called_with("skalevel", 1)


def test_read_attr():
    with mock.patch.object(
        TangoServerHelper, "get_instance", return_value=Mock()
    ):
        device_proxy = TangoServerHelper.get_instance()
        device_proxy.read_attr("Obstate")
        device_proxy.read_attr.assert_called_with("Obstate")


def test_write_attr():
    with mock.patch.object(
        TangoServerHelper, "get_instance", return_value=Mock()
    ):
        device_proxy = TangoServerHelper.get_instance()
        device_proxy.write_attr("Obstate", 1)
        device_proxy.write_attr.assert_called_with("Obstate", 1)
