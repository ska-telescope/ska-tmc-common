import enum
from typing import List, Tuple, Union

import tango
from ska_tango_base.commands import ResultCode

from ska_tmc_common.dev_factory import DevFactory


class AdapterType(enum.IntEnum):
    BASE = 0
    SUBARRAY = 1
    DISH = 2
    MCCS = 3
    CSPSUBARRAY = 4
    CSPMASTER = 5


class BaseAdapter:
    def __init__(self, dev_name: str, proxy: tango.DeviceProxy) -> None:
        self._proxy = proxy
        self._dev_name = dev_name

    @property
    def proxy(self) -> tango.DeviceProxy:
        return self._proxy

    @property
    def dev_name(self) -> str:
        return self._dev_name

    def On(self) -> None:
        self.proxy.On()

    def Off(self) -> None:
        self.proxy.Off()

    def Standby(self) -> None:
        self.proxy.Standby()

    def Reset(self) -> None:
        self.proxy.Reset()

    def Disable(self) -> None:
        self.proxy.Disable()


class CspMasterAdapter(BaseAdapter):
    def __init__(self, dev_name: str, proxy: tango.DeviceProxy) -> None:
        super().__init__(dev_name, proxy)

    def On(self, argin) -> None:
        self._proxy.On(argin)

    def Standby(self, argin) -> None:
        self._proxy.Standby(argin)

    def Off(self, argin) -> None:
        self._proxy.Off(argin)


class SubArrayAdapter(BaseAdapter):
    def __init__(self, dev_name: str, proxy: tango.DeviceProxy) -> None:
        super().__init__(dev_name, proxy)

    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.AssignResources(argin)

    def ReleaseAllResources(self) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.ReleaseAllResources()

    def ReleaseResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.ReleaseResources(argin)

    def Configure(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.Configure(argin)

    def Scan(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.Scan(argin)

    def EndScan(self) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.EndScan()

    def End(self) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.End()

    def Abort(self) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.Abort()

    def Restart(self) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.Restart()

    def ObsReset(self) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.ObsReset()


class MCCSAdapter(BaseAdapter):
    def __init__(self, dev_name: str, proxy: tango.DeviceProxy) -> None:
        super().__init__(dev_name, proxy)

    def AssignResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.AssignResources(argin)

    def ReleaseResources(
        self, argin: str
    ) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.ReleaseResources(argin)


class DishAdapter(BaseAdapter):
    def __init__(self, dev_name: str, proxy: tango.DeviceProxy) -> None:
        super().__init__(dev_name, proxy)

    def SetStandbyFPMode(self) -> None:
        self._proxy.SetStandbyFPMode()

    def SetOperateMode(self) -> None:
        self._proxy.SetOperateMode()

    def SetStandbyLPMode(self) -> None:
        self._proxy.SetStandbyLPMode()

    def SetStowMode(self) -> None:
        self._proxy.SetStowMode()

    def Configure(self, argin: str) -> None:
        self._proxy.Configure(argin)

    def ConfigureBand1(self, argin: str) -> None:
        self._proxy.ConfigureBand1(argin)

    def ConfigureBand2(self, argin: str) -> None:
        self._proxy.ConfigureBand2(argin)

    def ConfigureBand3(self, argin: str) -> None:
        self._proxy.ConfigureBand3(argin)

    def ConfigureBand4(self, argin: str) -> None:
        self._proxy.ConfigureBand4(argin)

    def ConfigureBand5a(self, argin: str) -> None:
        self._proxy.ConfigureBand5a(argin)

    def ConfigureBand5b(self, argin: str) -> None:
        self._proxy.ConfigureBand5b(argin)

    def Track(self) -> None:
        self._proxy.Track()

    def TrackStop(self) -> None:
        self._proxy.TrackStop()

    def Scan(self) -> None:
        self._proxy.Scan()

    def Restart(self) -> None:
        self._proxy.Restart()

    def AbortCommands(self) -> None:
        self._proxy.AbortCommands()

    def ObsReset(self) -> None:
        self._proxy.ObsReset()


class CspSubarrayAdapter(SubArrayAdapter):
    def __init__(self, dev_name: str, proxy: tango.DeviceProxy) -> None:
        super().__init__(dev_name, proxy)

    def End(self) -> Tuple[List[ResultCode], List[str]]:
        return self._proxy.GoToIdle()


class AdapterFactory:
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
