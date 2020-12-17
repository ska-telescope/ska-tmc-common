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


def test_set_status():
    tango_server_obj = TangoServerHelper()
    result = tango_server_obj.set_status("Working")
    print("result is :::::", result)
    assert 0
