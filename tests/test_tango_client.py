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


from src.tmc.common.tango_client import TangoClient

def test_dummy_function():
    print ("Dummy test")
    assert True

@pytest.fixture(scope="function")
def mock_lower_devices():
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    sdp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/sdp_subarray01'
    sdp_subarray1_fqdn = 'mid_sdp/elt/subarray_1'
    dish_ln_prefix = 'ska_mid/tm_leaf_node/d'

    dut_properties = {
        'CspSubarrayLNFQDN': csp_subarray1_ln_fqdn,
        'CspSubarrayFQDN': csp_subarray1_fqdn,
        'SdpSubarrayLNFQDN': sdp_subarray1_ln_fqdn,
        'SdpSubarrayFQDN': sdp_subarray1_fqdn,
        'DishLeafNodePrefix': dish_ln_prefix
    }

    csp_subarray1_ln_proxy_mock = Mock()
    csp_subarray1_proxy_mock = Mock()
    sdp_subarray1_ln_proxy_mock = Mock()
    sdp_subarray1_proxy_mock = Mock()
    dish_ln_proxy_mock = Mock()

    proxies_to_mock = {
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock,
        csp_subarray1_fqdn: csp_subarray1_proxy_mock,
        sdp_subarray1_ln_fqdn: sdp_subarray1_ln_proxy_mock,
        sdp_subarray1_fqdn: sdp_subarray1_proxy_mock,
        dish_ln_prefix + "0001": dish_ln_proxy_mock
    }

    event_subscription_map = {}
    dish_pointing_state_map = {}

    sdp_subarray1_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    csp_subarray1_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    csp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    sdp_subarray1_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: event_subscription_map.
            update({attr_name: callback}))

    dish_ln_proxy_mock.subscribe_event.side_effect = (
        lambda attr_name, event_type, callback, *args, **kwargs: dish_pointing_state_map.
            update({attr_name: callback}))

    with fake_tango_system(TangoClient, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map


# def test_proxy_creation(mock_lower_devices):
#     tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices

#     #csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
#     tango_client_obj = TangoClient(csp_subarray1_ln_proxy_mock)
#     device_proxy = tango_client_obj.get_deviceproxy()
#     print("device_proxy {} and its type {} is ::::::".format(device_proxy,type(device_proxy)))

#@pytest.mark.xfail
def test_get_fqdn():
    #tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
    csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
       
    csp_subarray1_ln_proxy_mock = Mock()

    proxies_to_mock = {  
        csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock
    }
    
    with mock.patch.object(TangoClient, 'get_deviceproxy', return_value=Mock()) as mock_obj:
        # patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
    
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
        # patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())

        tango_client_obj = TangoClient(csp_subarray1_ln_fqdn)
        device_fqdn1 = tango_client_obj.get_deviceproxy()
        # print("Device proxy is: {} and it type is: {}".format(device_fqdn1, type(device_fqdn1)))
        assert device_fqdn1 != None

def test_send_command():
    # tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
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
        tango_client_obj.send_command_async("End")
    # csp_subarray1_ln_proxy_mock.command_inout_async.assert_called_with("End")
        result = tango_client_obj.send_command_async("End")
        assert result == True
    # deviceproxy.command_inout_async.assert_called_with("End")

def test_get_attribute():
    # tango_context, csp_subarray1_ln_proxy_mock, csp_subarray1_proxy_mock, sdp_subarray1_ln_proxy_mock, sdp_subarray1_proxy_mock, dish_ln_proxy_mock, csp_subarray1_ln_fqdn, csp_subarray1_fqdn, sdp_subarray1_ln_fqdn, sdp_subarray1_fqdn, dish_ln_prefix, event_subscription_map, dish_pointing_state_map = mock_lower_devices
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

# @contextlib.contextmanager
# def fake_tango_system(device_under_test, initial_dut_properties={}, proxies_to_mock={},
#                       device_proxy_import_path='tango.DeviceProxy'):

#     with mock.patch(device_proxy_import_path) as patched_constructor:
#         patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
#         patched_module = importlib.reload(sys.modules[device_under_test.__module__])

#     device_under_test = getattr(patched_module, device_under_test.__name__)

#     device_test_context = DeviceTestContext(device_under_test, properties=initial_dut_properties)
#     device_test_context.start()
#     yield device_test_context
#     device_test_context.stop()
