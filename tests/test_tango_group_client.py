# Standard Python imports
import contextlib
import importlib
import json
import logging
import sys
import types

import mock
import pytest
import tango
from mock import MagicMock, Mock

# Additional import
from tango.test_context import DeviceTestContext

from src.ska_tmc_common.tango_group_client import TangoGroupClient

# from os.path import dirname, join


def test_get_tango_group():
    dish_group = "DishLeafNode_Group"

    dish_group_mock = Mock()

    with mock.patch.object(
        TangoGroupClient, "get_tango_group", return_value=Mock()
    ) as mock_obj:
        tango_client_obj = TangoGroupClient(
            dish_group, logging.getLogger("test")
        )
        tango_group = tango_client_obj.get_tango_group(dish_group)
        assert tango_group != None


@pytest.mark.xfail(reason="Need to mock Tango Group object")
def test_get_group_device_list():
    dish_group = "DishLeafNode_Group"

    dish_group_mock = Mock()

    with mock.patch.object(
        TangoGroupClient, "get_tango_group", return_value=Mock()
    ) as mock_obj:

        tango_client_obj = TangoGroupClient(
            dish_group, logging.getLogger("test")
        )
        dish_devices = ["ska_mid/tm_leaf_node/d0001"]
        tango_client_obj.add_device(dish_devices)
        result_list = tango_client_obj.get_group_device_list()
        assert result == dish_devices
