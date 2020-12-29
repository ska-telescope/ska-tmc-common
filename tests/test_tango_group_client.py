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
# from os.path import dirname, join

# Additional import
from tango.test_context import DeviceTestContext
from src.tmc.common.tango_group_client import TangoGroupClient


def test_get_tango_group():
    dish_group = 'DishLeafNode_Group'
       
    dish_group_mock = Mock()

    # groups_to_mock = {
    #     dish_group: dish_group_mock
    # }
    with mock.patch.object(TangoGroupClient, 'get_tango_group', return_value=Mock()) as mock_obj:
        tango_client_obj = TangoGroupClient(dish_group)
        tango_group = tango_client_obj.get_tango_group(dish_group)
        assert tango_group != None

pytest.mark.xfail(reason="Need to mock Tango Group object")
def test_get_group_device_list():
    dish_group = 'DishLeafNode_Group'

    dish_group_mock = Mock()

    # groups_to_mock = {
    #     dish_group: dish_group_mock
    # }    
    with mock.patch.object(TangoGroupClient, 'get_tango_group', return_value=Mock()) as mock_obj:
    
        tango_client_obj = TangoGroupClient(dish_group)
        dish_devices = ["ska_mid/tm_leaf_node/d0001"]
        tango_client_obj.add_device(dish_devices)
        result_list = tango_client_obj.get_group_device_list()
        assert result == dish_devices