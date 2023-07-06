"""
This module creates and manages different
functions of adapters by creating proxy for devices.
"""
import enum
from typing import List, Tuple, Union

import tango
from ska_tango_base.commands import ResultCode

from ska_tmc_common.dev_factory import DevFactory


class AdapterType(enum.IntEnum):
    """
    This class assigns enum value to different adapters.
    """

    BASE = 0
    SUBARRAY = 1
    DISH = 2
    MCCS = 3
    CSPSUBARRAY = 4
    CSPMASTER = 5
    SDPSUBARRAY = 6


class BaseAdapter:
    """
    It is base class used in creating adapters.
    """

    def __init__(self, dev_name: str, proxy: tango.DeviceProxy) -> None:
        self._proxy = proxy
        self._dev_name = dev_name

    @property
    def proxy(self) -> tango.DeviceProxy:
        """
        Sets proxy of device
        """
        return self._proxy

    @property
    def dev_name(self) -> str:
        """
        Returns device name.
        """
        return self._dev_name

    def On(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Sets device proxies to ON state.
        """
        return self.proxy.On()

    def Off(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Sets device proxies to OFF state.
        """
        return self.proxy.Off()

    def Standby(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Sets device proxies to Standby state.
        """
        return self.proxy.Standby()

    def Reset(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Sets device proxies to Reset state.
        """
        return self.proxy.Reset()

    def Disable(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Sets device proxies to Disable state.
        """
        return self.proxy.Disable()


class CspMasterAdapter(BaseAdapter):
    """
    This class is used for creating and managing adapterss
    for CSP master devices.
    """

    def On(self, argin) -> Tuple[List[ResultCode], List[str]]:
        """
        Sets device proxies to ON state
        """
        self._proxy.On(argin)

    def Standby(self, argin) -> Tuple[List[ResultCode], List[str]]:
        """
        Sets device proxiesto Standby state
        """
        self._proxy.Standby(argin)

    def Off(self, argin) -> Tuple[List[ResultCode], List[str]]:
        """
        Sets device proxies to Off state
        """
        self._proxy.Off(argin)


class SubArrayAdapter(BaseAdapter):
    """
    This class is used for creating and managing adapters
    for Subarray devices.
    """

    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes AssignResources on subarray device proxy.
        """
        return self._proxy.AssignResources(argin)

    def ReleaseAllResources(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ReleaseAllResources on subarray device proxy.
        """
        return self._proxy.ReleaseAllResources()

    def ReleaseResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ReleaseResources on subarray device proxy.
        """
        return self._proxy.ReleaseResources(argin)

    def Configure(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Configure on subarray device proxy.
        """
        return self._proxy.Configure(argin)

    def Scan(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Scan on subarray device proxy.
        """
        return self._proxy.Scan(argin)

    def EndScan(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes EndScan on subarray device proxy.
        """
        return self._proxy.EndScan()

    def End(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes End on subarray device proxy.
        """
        return self._proxy.End()

    def Abort(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Abort on subarray device proxy.
        """
        return self._proxy.Abort()

    def Restart(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Restart on subarray device proxy.
        """
        return self._proxy.Restart()

    def ObsReset(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Reset on subarray device proxy.
        """
        return self._proxy.ObsReset()


class SdpSubArrayAdapter(SubArrayAdapter):
    """
    This class is used for creating and managing adapters
    for SdpSubarray devices.
    """

    def AssignResources(
        self, argin: str, callback
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes AssignResources on SdpSubarray device proxy.
        """
        return self._proxy.command_inout_asynch(
            "AssignResources", argin, callback
        )

    def ReleaseAllResources(
        self, callback
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ReleaseAllResources on SdpSubarray device proxy.
        """
        return self._proxy.command_inout_asynch(
            "ReleaseAllResources", callback
        )


class MCCSAdapter(BaseAdapter):
    """
    This class is used for creating and managing adapterss
    for MCCS devices.
    """

    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes AssignResources on device proxy.
        """
        return self._proxy.AssignResources(argin)

    def ReleaseResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ReleaseResources on device proxy.
        """
        return self._proxy.ReleaseResources(argin)


class DishAdapter(BaseAdapter):
    """
    This class is used for creating and managing adapters
    for Dishes proxy.
    """

    def SetStandbyFPMode(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes SetStandbyFPMode on device proxy.
        """
        return self._proxy.SetStandbyFPMode()

    def SetOperateMode(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes SetOperateMode on device proxy.
        """
        return self._proxy.SetOperateMode()

    def SetStandbyLPMode(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes SetStandbyLPMode on device proxy.
        """
        return self._proxy.SetStandbyLPMode()

    def SetStowMode(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes SetStowMode on device proxy.
        """
        return self._proxy.SetStowMode()

    def Configure(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Configure on device proxy.
        """
        return self._proxy.Configure(argin)

    def ConfigureBand1(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ConfigureBand1 on device proxy.
        """
        return self._proxy.ConfigureBand1(argin)

    def ConfigureBand2(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ConfigureBand2 on device proxy.
        """
        return self._proxy.ConfigureBand2(argin)

    def ConfigureBand3(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ConfigureBand3 on device proxy.
        """
        return self._proxy.ConfigureBand3(argin)

    def ConfigureBand4(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ConfigureBand4 on device proxy.
        """
        return self._proxy.ConfigureBand4(argin)

    def ConfigureBand5a(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ConfigureBand5a on device proxy.
        """
        return self._proxy.ConfigureBand5a(argin)

    def ConfigureBand5b(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ConfigureBand5b on device proxy.
        """
        return self._proxy.ConfigureBand5b(argin)

    def Track(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Track on device proxy.
        """
        return self._proxy.Track()

    def TrackStop(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes TrackStop on device proxy.
        """
        return self._proxy.TrackStop()

    def Scan(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Scan on device proxy.
        """
        return self._proxy.Scan()

    def Restart(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Restart on device proxy.
        """
        return self._proxy.Restart()

    def AbortCommands(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Abort on device proxy.
        """
        return self._proxy.AbortCommands()

    def ObsReset(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Reset on device proxy.
        """
        return self._proxy.ObsReset()

    def Reset(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Reset on device proxy.
        """
        return self._proxy.Reset()


class CspSubarrayAdapter(SubArrayAdapter):
    """
    This class is used for creating and managing adapterss
    for CSP subarray devices proxy.
    """

    def End(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes End on device proxy.
        """
        return self._proxy.GoToIdle()


class AdapterFactory:
    """
    This class is used for creating and managing adapterss
    for CSP subarray devices .
    """

    def __init__(self) -> None:
        self.adapters = []
        self._dev_factory = DevFactory()

    def get_or_create_adapter(
        self, dev_name: str, adapter_type: AdapterType = AdapterType.BASE
    ) -> Union[
        DishAdapter,
        SubArrayAdapter,
        CspMasterAdapter,
        CspSubarrayAdapter,
        SdpSubArrayAdapter,
        MCCSAdapter,
        BaseAdapter,
    ]:
        """
        Get a generic adapter for a device if already created
        or create new adapter as per the device type and add to adpter list

        :param dev_name: device name

        :type str
        """

        for adapter in self.adapters:
            if adapter.dev_name == dev_name:
                return adapter

        new_adapter = None
        if adapter_type == AdapterType.DISH:
            new_adapter = DishAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )
        elif adapter_type == AdapterType.SUBARRAY:
            new_adapter = SubArrayAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )
        elif adapter_type == AdapterType.CSPSUBARRAY:
            new_adapter = CspSubarrayAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )
        elif adapter_type == AdapterType.SDPSUBARRAY:
            new_adapter = SdpSubArrayAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )
        elif adapter_type == AdapterType.MCCS:
            new_adapter = MCCSAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )
        elif adapter_type == AdapterType.CSPMASTER:
            new_adapter = CspMasterAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )
        else:
            new_adapter = BaseAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )

        self.adapters.append(new_adapter)
        return new_adapter
