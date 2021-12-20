# Standard Python imports
import logging

import mock
import pytest
from mock import Mock

# Additional import
from src.ska_tmc_common.tango_client import TangoClient


def test_get_fqdn():
    csp_subarray1_ln_fqdn = "ska_mid/tm_leaf_node/csp_subarray01"
    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ):
        tango_client_obj = TangoClient(
            csp_subarray1_ln_fqdn, logging.getLogger("test")
        )
        device_fqdn = tango_client_obj.get_device_fqdn()
        assert device_fqdn == "ska_mid/tm_leaf_node/csp_subarray01"


def test_get_device_proxy():
    csp_subarray1_ln_fqdn = "ska_mid/tm_leaf_node/csp_subarray01"
    # csp_subarray1_ln_proxy_mock = Mock()

    # proxies_to_mock = {csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock}

    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ):
        tango_client_obj = TangoClient(
            csp_subarray1_ln_fqdn, logging.getLogger("test")
        )
        device_proxy = tango_client_obj._get_deviceproxy()
        assert device_proxy is not None


@pytest.mark.xfail(reason="Need to mock Tango DeviceProxy object")
def test_send_command():
    csp_subarray1_ln_fqdn = "ska_mid/tm_leaf_node/csp_subarray01"
    device_proxy = Mock()

    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=device_proxy
    ):
        tango_client_obj = TangoClient(
            csp_subarray1_ln_fqdn, logging.getLogger("test")
        )
        device_proxy = tango_client_obj._get_deviceproxy()
        result = tango_client_obj.send_command("End")
        assert result is True


@pytest.mark.xfail(reason="Need to mock Tango DeviceProxy object")
def test_get_attribute():
    csp_subarray1_ln_fqdn = "ska_mid/tm_leaf_node/csp_subarray01"
    # deviceproxy = Mock()
    # csp_subarray1_ln_proxy_mock = Mock()

    # proxies_to_mock = {csp_subarray1_ln_fqdn: csp_subarray1_ln_proxy_mock}

    with mock.patch.object(
        TangoClient, "_get_deviceproxy", return_value=Mock()
    ):
        tango_client_obj = TangoClient(
            csp_subarray1_ln_fqdn, logging.getLogger("test")
        )
        # device_proxy = tango_client_obj._get_deviceproxy()
        result = tango_client_obj.get_attribute("DummyAttribute")
        assert result is True
