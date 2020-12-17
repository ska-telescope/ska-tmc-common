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
from src.tmc.common.tango_group_client import TangoGroupClient


def test_dummy_function():
    print ("Dummy test")
    assert True


def test_send_command_tango_group():
    #csp_subarray1_ln_fqdn = 'ska_mid/tm_leaf_node/csp_subarray01'
    dish_group = 'DishLeafNode_Group'
    dish_group_mock = Mock()

    groups_to_mock = {
        dish_group: dish_group_mock
    }    

    with mock.patch.object(TangoGroupClient, 'get_tango_group', return_value=Mock()) as mock_obj:
        tango_client_obj = TangoGroupClient(dish_group)
        tango_group = tango_client_obj.get_tango_group()
        print("tango_group is: {} and it type is: {}".format(tango_group, type(tango_group)))
        tango_client_obj.send_command("End")
        result = tango_client_obj.send_command("End")
        assert result == True

def test_get_tango_group():
    dish_group = 'DishLeafNode_Group'
       
    dish_group_mock = Mock()

    groups_to_mock = {
        dish_group: dish_group_mock
    }    
    with mock.patch.object(TangoGroupClient, 'get_tango_group', return_value=Mock()) as mock_obj:
    
        tango_client_obj = TangoGroupClient(dish_group)
        tango_group = tango_client_obj.get_tango_group()
        print("tango_group is: {} and it type is: {}".format(tango_group, type(tango_group)))
        assert tango_group == 'DishLeafNode_Group'
