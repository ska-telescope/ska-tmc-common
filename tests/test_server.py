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
from src.tmc.common.tango_server import TangoServerHelper


def test_get_instance():
    with mock.patch.object(TangoServerHelper, 'get_instance', return_value=Mock()) as mock_obj:
        device_proxy = TangoServerHelper.get_instance()
        device_proxy.Status = "Testing status for mock device"
        device_proxy.set_status("Testing status for mock device")
        device_proxy.set_status.assert_called_with("Testing status for mock device")

