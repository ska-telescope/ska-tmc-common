"""
This module defines classes/methods that manage
the adapters required to communicate with various devices.
"""
from typing import Any, Optional, Union

import mock
from tango import DeviceProxy

from ska_tmc_common.adapters import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    CspMasterAdapter,
    CspSubarrayAdapter,
    DishAdapter,
    MCCSAdapter,
    SubArrayAdapter,
)


class HelperAdapterFactory(AdapterFactory):
    """
    This class to create various types of adapters for various devices
    """

    def __init__(self) -> None:
        super().__init__()
        self.adapters = []

    def get_or_create_adapter(
        self,
        dev_name: str,
        adapter_type: AdapterType = AdapterType.BASE,
        proxy: Optional[DeviceProxy] = None,
        attrs: Any = None,
    ) -> Union[
        DishAdapter,
        SubArrayAdapter,
        CspMasterAdapter,
        CspSubarrayAdapter,
        MCCSAdapter,
        BaseAdapter,
    ]:
        """
        Method to create adapter for different devices
        :param dev_name: device name
        :param adapter_type: type of adapter
        :param proxy : Device proxy

        :return: new_adapter
        :rtype: Union
        """
        if proxy is None:
            proxy = mock.Mock(attrs)

        for adapter in self.adapters:
            if adapter.dev_name == dev_name:
                return adapter

        new_adapter = None
        if adapter_type == AdapterType.DISH:
            new_adapter = DishAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.SUBARRAY:
            new_adapter = SubArrayAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.MCCS:
            new_adapter = MCCSAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.CSPSUBARRAY:
            new_adapter = CspSubarrayAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.CSPMASTER:
            new_adapter = CspMasterAdapter(dev_name, proxy)
        else:
            new_adapter = BaseAdapter(dev_name, proxy)

        self.adapters.append(new_adapter)
        return new_adapter
