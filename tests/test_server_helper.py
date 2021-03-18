# Standard Python imports
import contextlib
import importlib
import sys
import json
import types
import pytest
import tango
import mock
from mock import Mock
from mock import MagicMock
from os.path import dirname, join

#Additional imports
from tango.test_context import DeviceTestContext
from src.tmc.common.tango_server_helper import TangoServerHelper


def test_set_status():
    with mock.patch.object(TangoServerHelper, 'get_instance', return_value=Mock()) as mock_obj:
        device_proxy = TangoServerHelper.get_instance()
        device_proxy.Status = "Testing status for mock device"
        device_proxy.set_status("Testing status for mock device")
        device_proxy.set_status.assert_called_with("Testing status for mock device")


def test_get_status():
    with mock.patch.object(TangoServerHelper, 'get_instance', return_value=Mock()) as mock_obj:
        device_proxy = TangoServerHelper.get_instance()
        device_proxy.get_status()
        device_proxy.get_status.assert_called_with()


def test_read_attr():
    with mock.patch.object(TangoServerHelper, 'get_instance', return_value=Mock()) as mock_obj:
        device_proxy = TangoServerHelper.get_instance()
        device_proxy.read_attr("Obstate")
        device_proxy.read_attr.assert_called_with("Obstate")


def test_write_attr():
    with mock.patch.object(TangoServerHelper, 'get_instance', return_value=Mock()) as mock_obj:
        device_proxy = TangoServerHelper.get_instance()
        device_proxy.write_attr("Obstate", 1)
        device_proxy.write_attr.assert_called_with("Obstate", 1)
