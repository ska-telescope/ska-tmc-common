# Standard Python imports
import logging

import mock
import pytest
from mock import Mock

# Additional import
from ska_tmc_common import TangoGroupClient


def test_get_tango_group():
    dish_group = "DishLeafNode_Group"

    # dish_group_mock = Mock()

    with mock.patch.object(
        TangoGroupClient, "get_tango_group", return_value=Mock()
    ):
        tango_client_obj = TangoGroupClient(
            dish_group, logging.getLogger("test")
        )
        assert tango_client_obj.tango_group is not None


@pytest.mark.xfail(reason="Need to mock Tango Group object")
def test_get_group_device_list():
    dish_group = "DishLeafNode_Group"

    # dish_group_mock = Mock()

    with mock.patch.object(
        TangoGroupClient, "get_tango_group", return_value=Mock()
    ):

        tango_client_obj = TangoGroupClient(
            dish_group, logging.getLogger("test")
        )
        dish_device = "ska_mid/tm_leaf_node/d0001"
        tango_client_obj.add_device(dish_device)
        result_list = tango_client_obj.get_group_device_list()
        assert result_list is dish_device
