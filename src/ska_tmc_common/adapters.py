import enum

from dev_factory import DevFactory


class AdapterType(enum.IntEnum):
    BASE = 0
    SUBARRAY = 1
    DISH = 2


class AdapterFactory:
    def __init__(self) -> None:
        self._adapters = []
        self._dev_factory = DevFactory()

    def get_or_create_adapter(self, dev_name, adapter_type=AdapterType.BASE):
        """
        Get a generic adapter for a device if already created
        or create new adapter as per the device type and add to adpter list

        :param dev_name: device name
        :type str
        """
        for adapter in self._adapters:
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
        else:
            new_adapter = BaseAdapter(
                dev_name, self._dev_factory.get_device(dev_name)
            )

        self._adapters.append(new_adapter)
        return new_adapter


class BaseAdapter:
    def __init__(self, dev_name, proxy) -> None:
        self._proxy = proxy
        self._dev_name = dev_name

    @property
    def proxy(self):
        return self._proxy

    @property
    def dev_name(self):
        return self._dev_name

    def On(self):
        self.proxy.TelescopeOn()

    def Off(self):
        self.proxy.TelescopeOff()

    def StandBy(self):
        self.proxy.TelescopeStandBy()
