# Standard Python imports
import contextlib
import importlib
import sys
import json
import types
import pytest
import tango
# import mock
from mock import Mock
from mock import MagicMock
from os.path import dirname, join
imporrt logging
logging.getLogger('tcpserver')
# Additional import

from tango.test_context import DeviceTestContext
from src.tmc.common.tango_client import TangoClient


def test_get_fqdn():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        tango_client_obj = TangoClient(csp_subarray1_ln_fqdn, logging.getLogger('test'))
        device_fqdn = tango_client_obj.get_device_fqdn()
        assert device_fqdn == 'ska_mid/tm_leaf_node/csp_subarray01'


def test_get_device_proxy():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock
    }

    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        tango_client_obj = TangoClient(csp_subarray1_ln_fqdn, logging.getLogger('test'))
        device_proxy = tango_client_obj._get_deviceproxy()
        assert device_proxy != None

@pytest.mark.xfail(reason="Need to mock Tango DeviceProxy object")
def test_send_command():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    device_proxy = Mock()

    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=device_proxy) as mock_obj:
        tango_client_obj = TangoClient(csp_subarray1_ln_fqdn, logging.getLogger('test'))
        device_proxy = tango_client_obj._get_deviceproxy()
        result = tango_client_obj.send_command("End")
        assert result == True

@pytest.mark.xfail(reason="Need to mock Tango DeviceProxy object")
def test_get_attribute():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    # deviceproxy = Mock()
    csp_subarray1_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock
    }

    with mock.patch.object(TangoClient, '_get_deviceproxy', return_value=Mock()) as mock_obj:
        tango_client_obj = TangoClient(csp_subarray1_ln_fqdn, logging.getLogger('test'))
        device_proxy = tango_client_obj._get_deviceproxy()
        result = tango_client_obj.get_attribute("DummyAttribute")
        assert result == True

# def any_method(with_name=None):
#     class AnyMethod():
#         def __eq__(self, other):
#             if not isinstance(other, types.MethodType):
#                 return False

#             return other.__func__.__name__ == with_name if with_name else True

#     return AnyMethod()
