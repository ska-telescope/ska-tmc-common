"""
This module manages to create and manages adaptor.
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
    This class manages to create and manages adaptor.
    """

    def __init__(self) -> None:
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
        Method to create adaptor for different devices
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
