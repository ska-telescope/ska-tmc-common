"""
This module defines classes/methods that manage
the adapters required to communicate with various devices.
"""
import logging
from typing import Any, Optional, Union

from ska_ser_logging.configuration import configure_logging
from tango import DeviceProxy

from ska_tmc_common.adapters import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    CspMasterAdapter,
    CspMasterLeafNodeAdapter,
    CspSubarrayAdapter,
    DishAdapter,
    DishLeafAdapter,
    MCCSControllerAdapter,
    MCCSMasterLeafNodeAdapter,
    SdpSubArrayAdapter,
    SubarrayAdapter,
)

configure_logging()
logger = logging.getLogger(__name__)


class HelperAdapterFactory(AdapterFactory):
    """
    This class to create various types of adapters for various devices
    """

    def __init__(self) -> None:
        super().__init__()
        self.adapters = []

    # pylint: disable=unused-argument
    def get_or_create_adapter(
        self,
        dev_name: str,
        adapter_type: AdapterType = AdapterType.BASE,
        proxy: Optional[DeviceProxy] = None,
        attrs: Any = None,
    ) -> Union[
        DishAdapter,
        DishLeafAdapter,
        SubarrayAdapter,
        CspMasterAdapter,
        CspSubarrayAdapter,
        MCCSMasterLeafNodeAdapter,
        MCCSControllerAdapter,
        BaseAdapter,
        SdpSubArrayAdapter,
        CspMasterLeafNodeAdapter,
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
            proxy = self._dev_factory.get_device(dev_name)
            logger.debug("The proxy for device %s is created", dev_name)
        for adapter in self.adapters:
            if adapter.dev_name == dev_name:
                logger.debug(
                    "The adapter is created for device name %s",
                    adapter.dev_name,
                )
                return adapter

        new_adapter = None
        if adapter_type == AdapterType.DISH:
            new_adapter = DishAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.SUBARRAY:
            new_adapter = SubarrayAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.MCCS_MASTER_LEAF_NODE:
            new_adapter = MCCSMasterLeafNodeAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.MCCS_CONTROLLER:
            new_adapter = MCCSControllerAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.CSPSUBARRAY:
            new_adapter = CspSubarrayAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.CSPMASTER:
            new_adapter = CspMasterAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.SDPSUBARRAY:
            new_adapter = SdpSubArrayAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.CSP_MASTER_LEAF_NODE:
            new_adapter = CspMasterLeafNodeAdapter(dev_name, proxy)
        elif adapter_type == AdapterType.DISH_LEAF_NODE:
            new_adapter = DishLeafAdapter(dev_name, proxy)
        else:
            new_adapter = BaseAdapter(dev_name, proxy)

        self.adapters.append(new_adapter)
        return new_adapter
