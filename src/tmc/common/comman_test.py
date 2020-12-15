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

from tango_client import TangoClient

@pytest.fixture(scope="function")
def mock_csp_subarray():
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray1_fqdn
    }
    csp_subarray1_proxy_mock = Mock()
    proxies_to_mock = {
        csp_subarray1_fqdn: csp_subarray1_proxy_mock
    }
    with fake_tango_system(TangoClient, initial_dut_properties=dut_properties,
                           proxies_to_mock=proxies_to_mock) as tango_context:
        yield tango_context.device, csp_subarray1_proxy_mock, csp_subarray1_fqdn

def test_proxy_creation():
    # device_proxy, csp_subarray1_proxy_mock, csp_subarray1_fqdn = mock_csp_subarray
    # csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    # TangoClient(csp_subarray1_fqdn)
    csp_subarray1_fqdn = 'mid_csp/elt/subarray_01'
    dut_properties = {
        'CspSubarrayFQDN': csp_subarray1_fqdn
    }
    csp_subarray1_proxy_mock = Mock()
    proxies_to_mock = {
        csp_subarray1_fqdn: csp_subarray1_proxy_mock
    }
    with fake_tango_system(TangoClient, initial_dut_properties=dut_properties, proxies_to_mock=proxies_to_mock) as tango_context:
        tango_context.device(csp_subarray1_fqdn)
        # TangoClient(csp_subarray1_fqdn)
        # b = a.get_device_fqdn()
        tango_context.device.send_command("End")
        print("b {} and its type {} is ::::::".format(b,type(b)))


def fake_tango_system(device_under_test, initial_dut_properties={}, proxies_to_mock={},
                      device_proxy_import_path='tango.DeviceProxy'):
    with mock.patch(device_proxy_import_path) as patched_constructor:
        patched_constructor.side_effect = lambda device_fqdn: proxies_to_mock.get(device_fqdn, Mock())
        patched_module = importlib.reload(sys.modules[device_under_test.__module__])

    device_under_test = getattr(patched_module, device_under_test.__name__)

    device_test_context = DeviceTestContext(device_under_test, properties=initial_dut_properties)
    device_test_context.start()
    yield device_test_context
    device_test_context.stop()
# fake_tango_system(TangoClient, initial_dut_properties={}, proxies_to_mock={}, device_proxy_import_path='')
test_proxy_creation()
