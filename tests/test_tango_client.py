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

from src.tmc.common.tango_client import TangoClient

def test_dummy_function():
    print ("Dummy test")
    assert True

# def test_proxy_creation():
#     csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
#     tango_client_obj = TangoClient(csp_subarray1_fqdn)
#     device_proxy = tango_client_obj.get_deviceproxy()
#     print("device_proxy {} and its type {} is ::::::".format(device_proxy,type(device_proxy)))
#     assert 1

def test_get_fqdn():
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    tango_client_obj = TangoClient(csp_subarray1_fqdn)
    device_fqdn = tango_client_obj.get_device_fqdn()
    assert device_fqdn == 'mid_csp/elt/subarray_01'