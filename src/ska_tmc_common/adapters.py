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
    This class assigns enum value to different adaptor.
    """

    BASE = 0
    SUBARRAY = 1
    DISH = 2
    MCCS = 3
    CSPSUBARRAY = 4
    CSPMASTER = 5


class BaseAdapter:
    """
    It is base class used in creating adaptor.
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

    def On(self) -> None:
        """
        Sets device proxies to ON state.
        """
        self.proxy.On()

    def Off(self) -> None:
        """
        Sets device proxies to OFF state.
        """
        self.proxy.Off()

    def Standby(self) -> None:
        """
        Sets device proxies to Standby state.
        """
        self.proxy.Standby()

    def Reset(self) -> None:
        """
        Sets device proxies to Reset state.
        """
        self.proxy.Reset()

    def Disable(self) -> None:
        """
        Sets device proxies to Disable state.
        """
        self.proxy.Disable()


class CspMasterAdapter(BaseAdapter):
    """
    This class is used for creating and managing adaptors
    for CSP master devices.
    """

    def __init__(self, dev_name: str, proxy: tango.DeviceProxy) -> None:
        super().__init__(dev_name, proxy)

    def On(self, argin) -> None:
        """
        Sets device proxies to ON state
        """
        self._proxy.On(argin)

    def Standby(self, argin) -> None:
        """
        Sets device proxiesto Standby state
        """
        self._proxy.Standby(argin)

    def Off(self, argin) -> None:
        """
        Sets device proxies to Off state
        """
        self._proxy.Off(argin)


class SubArrayAdapter(BaseAdapter):
    """
    This class is used for creating and managing adaptors
    for Subarray devices.
    """

    def __init__(self, dev_name: str, proxy: tango.DeviceProxy) -> None:
        super().__init__(dev_name, proxy)

    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes AssignResources on subarray device proxies.
        """
        return self._proxy.AssignResources(argin)

    def ReleaseAllResources(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ReleaseAllResources on subarray device proxies.
        """
        return self._proxy.ReleaseAllResources()

    def ReleaseResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ReleaseResources on subarray device proxies.
        """
        return self._proxy.ReleaseResources(argin)

    def configure(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Configure on subarray device proxies.
        """
        return self._proxy.configure(argin)

    def Scan(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Scan on subarray device proxies.
        """
        return self._proxy.Scan(argin)

    def EndScan(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes EndScan on subarray device proxies.
        """
        return self._proxy.EndScan()

    def End(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes End on subarray device proxies.
        """
        return self._proxy.End()

    def Abort(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Abort on subarray device proxies.
        """
        return self._proxy.Abort()

    def Restart(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Restart on subarray device proxies.
        """
        return self._proxy.Restart()

    def ObsReset(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes Reset on subarray device proxies.
        """
        return self._proxy.ObsReset()


class MCCSAdapter(BaseAdapter):
    """
    This class is used for creating and managing adaptors
    for MCCS devices.
    """

    def __init__(self, dev_name: str, proxy: tango.DeviceProxy) -> None:
        super().__init__(dev_name, proxy)

    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes AssignResources on device proxies.
        """
        return self._proxy.AssignResources(argin)

    def ReleaseResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes ReleaseResources on device proxies.
        """
        return self._proxy.ReleaseResources(argin)


class DishAdapter(BaseAdapter):
    """
    This class is used for creating and managing adaptors
    for Dishes proxies.
    """

    def __init__(self, dev_name: str, proxy: tango.DeviceProxy) -> None:
        super().__init__(dev_name, proxy)

    def SetStandbyFPMode(self) -> None:
        """
        Invokes StandBy on device proxies.
        """
        self._proxy.SetStandbyFPMode()

    def SetOperateMode(self) -> None:
        """
        Invokes Operator on device proxies.
        """
        self._proxy.SetOperateMode()

    def SetStandbyLPMode(self) -> None:
        """
        Invokes Standby on device proxies.
        """
        self._proxy.SetStandbyLPMode()

    def SetStowMode(self) -> None:
        """
        Invokes Stow on device proxies.
        """
        self._proxy.SetStowMode()

    def configure(self, argin: str) -> None:
        """
        Invokes configure on device proxies.
        """
        self._proxy.configure(argin)

    def configure_band1(self, argin: str) -> None:
        """
        Invokes configure on device proxies.
        """
        self._proxy.configure_band1(argin)

    def configure_band2(self, argin: str) -> None:
        """
        Invokes configure on device proxies.
        """
        self._proxy.configure_band2(argin)

    def configure_band3(self, argin: str) -> None:
        """
        Invokes configure on device proxies.
        """
        self._proxy.configure_band3(argin)

    def configure_band4(self, argin: str) -> None:
        """
        Invokes configure on device proxies.
        """
        self._proxy.configure_band4(argin)

    def configure_band5a(self, argin: str) -> None:
        """
        Invokes configure on device proxies.
        """
        self._proxy.configure_band5a(argin)

    def configure_band5b(self, argin: str) -> None:
        """
        Invokes configure on device proxies.
        """
        self._proxy.configure_band_5b(argin)

    def Track(self) -> None:
        """
        Invokes Track on device proxies.
        """
        self._proxy.Track()

    def TrackStop(self) -> None:
        """
        Invokes TrackStop on device proxies.
        """
        self._proxy.TrackStop()

    def Scan(self) -> None:
        """
        Invokes Scan on device proxies.
        """
        self._proxy.Scan()

    def Restart(self) -> None:
        """
        Invokes Restart on device proxies.
        """
        self._proxy.Restart()

    def Abort(self) -> None:
        """
        Invokes Abort on device proxies.
        """
        self._proxy.AbortCommands()

    def ObsReset(self) -> None:
        """
        Invokes Reset on device proxies.
        """
        self._proxy.ObsReset()


class CspSubarrayAdapter(SubArrayAdapter):
    """
    This class is used for creating and managing adaptors
    for CSP subarray devices proxies.
    """

    def __init__(self, dev_name: str, proxy: tango.DeviceProxy) -> None:
        super().__init__(dev_name, proxy)

    def End(self) -> Tuple[List[ResultCode], List[str]]:
        """
        Invokes End on device proxies.
        """
        return self._proxy.GoToIdle()


class AdapterFactory:
    """
    This class is used for creating and managing adaptors
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
