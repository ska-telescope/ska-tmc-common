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
from tango.test_context import DeviceTestContext

# Additional import
# from cspsubarrayleafnode import CspSubarrayLeafNode, const, release
# from ska.base.control_model import HealthState, ObsState, LoggingLevel

from src.tmc.common.tango_client import TangoClient

def test_proxy_creation():
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    a = TangoClient(csp_subarray1_fqdn)
    b = TangoClient.get_deviceproxy()
    print("b {} and its type {} is ::::::".format(b,type(b)))
test_proxy_creation()