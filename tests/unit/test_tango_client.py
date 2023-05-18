# Standard Python imports
import logging

import mock
import pytest
from mock import Mock

# Additional import
from ska_tmc_common import TangoClient
from tests.conftest import csp_sln_dev_name


def test_get_fqdn(csp_sln_dev_name):
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ):
        tango_client_obj = TangoClient(
            csp_sln_dev_name, logging.getLogger("test")
        )
        device_fqdn = tango_client_obj.get_device_fqdn()
        assert device_fqdn == "ska_mid/tm_leaf_node/csp_subarray01"


def test_get_device_proxy(csp_sln_dev_name):

    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ):
        tango_client_obj = TangoClient(
            csp_sln_dev_name, logging.getLogger("test")
        )
        assert tango_client_obj.deviceproxy is not None


@pytest.mark.xfail(reason="Need to mock Tango DeviceProxy object")
def test_send_command():
    device_proxy = Mock()

    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=device_proxy
    ):
        tango_client_obj = TangoClient(
            csp_sln_dev_name, logging.getLogger("test")
        )
        result = tango_client_obj.send_command("End")
        assert result is True


@pytest.mark.xfail(reason="Need to mock Tango DeviceProxy object")
def test_get_attribute():
    # deviceproxy = Mock()
    # csp_subarray1_ln_proxy_mock = Mock()

    # proxies_to_mock = {csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock}

    with mock.patch.object(
        csp_sln_dev_name, TangoClient, "_get_deviceproxy", return_value=Mock()
    ):
        tango_client_obj = TangoClient(
            csp_sln_dev_name, logging.getLogger("test")
        )
        # device_proxy = tango_client_obj._get_deviceproxy()
        result = tango_client_obj.get_attribute("DummyAttribute")
        assert result is True
