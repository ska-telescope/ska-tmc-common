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

# Additional import

from tango.test_context import DeviceTestContext
from src.tmc.common.tango_client import TangoClient



def test_dummy_function():
    print ("Dummy test")
    assert True

def test_get_fqdn():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    with mock.patch.object(TangoClient, 'get_deviceproxy', return_value=Mock()) as mock_obj:
        tango_client_obj = TangoClient(csp_subarray1_ln_fqdn)
        device_fqdn1 = tango_client_obj.get_device_fqdn()
        assert device_fqdn1 == 'ska_mid/tm_leaf_node/csp_subarray01'


def test_get_device_prox():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock
    }

    with mock.patch.object(TangoClient, 'get_deviceproxy', return_value=Mock()) as mock_obj:
        tango_client_obj = TangoClient(csp_subarray1_ln_fqdn)
        device_fqdn1 = tango_client_obj.get_deviceproxy()
        assert device_fqdn1 != None

def test_send_command():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    device_proxy = Mock()

    with mock.patch.object(TangoClient, 'get_deviceproxy', return_value=device_proxy) as mock_obj:
        tango_client_obj = TangoClient(csp_subarray1_ln_fqdn)
        device_proxy = tango_client_obj.get_deviceproxy()
        result = tango_client_obj.send_command_async("End")
        assert result == True
        #TODO: Future reference
    # mock_obj.command_inout_async.assert_called_with("End", None)


def test_get_attribute():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    deviceproxy = Mock()
    csp_subarray1_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock
    }

    with mock.patch.object(TangoClient, 'get_deviceproxy', return_value=Mock()) as mock_obj:
        tango_client_obj = TangoClient(csp_subarray1_ln_fqdn)
        device_fqdn1 = tango_client_obj.get_deviceproxy()
        print("Device proxy is: {} and it type is: {}".format(device_fqdn1, type(device_fqdn1)))
        result = tango_client_obj.get_attribute("xyz")
        assert result == True
