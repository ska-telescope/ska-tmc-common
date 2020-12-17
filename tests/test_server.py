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

# Tango imports

# Additional import
# from cspsubarrayleafnode import CspSubarrayLeafNode, const, release
# from ska.base.control_model import HealthState, ObsState, LoggingLevel
from tango.test_context import DeviceTestContext
from src.tmc.common.tango_server import TangoServerHelper


def test_get_instance():
    device_proxy = Mock()

    with mock.patch.object(TangoServerHelper, 'get_instance', return_value=device_proxy) as mock_obj:
        tango_client_obj = TangoServerHelper()
        device_proxy = tango_client_obj.get_instance()
    # tango_server_obj = TangoServerHelper.get_instance()
    # result = tango_server_obj.set_status("Working")
        print("device_proxy is :::::", device_proxy)
        assert 0
