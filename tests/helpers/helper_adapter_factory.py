import mock

from ska_tmc_common.adapters import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    DishAdapter,
    MCCSAdapter,
    SubArrayAdapter,
)


class HelperAdapterFactory(AdapterFactory):
    def __init__(self) -> None:
        self.adapters = []

    def get_or_create_adapter(
        self, dev_name, adapter_type=AdapterType.BASE, proxy=None, attrs=None
    ):
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
        else:
            new_adapter = BaseAdapter(dev_name, proxy)

        self.adapters.append(new_adapter)
        return new_adapter