import logging
from typing import Optional

import pytest

from ska_tmc_common.adapters import AdapterType
from ska_tmc_common.enum import LivelinessProbeType
from ska_tmc_common.input import InputParameter
from ska_tmc_common.test_helpers.helper_adapter_factory import (
    HelperAdapterFactory,
)
from ska_tmc_common.tmc_command import TMCCommand
from ska_tmc_common.tmc_component_manager import TmcComponentManager
from tests.settings import logger


class StateDevice(TMCCommand):
    def __init__(
        self,
        dev_name: str,
        component_manager,
        logger: Optional[logging.Logger] = None,
        adapter_factory=None,
        *args,
        **kwargs
    ):
        super().__init__(component_manager, logger, *args, **kwargs)
        self.dev_name = dev_name
        self.adapter_factory = adapter_factory
        self.state_adapter = None
        self.init_adapters()

    def init_adapters(self):
        print("Initializing adapter")
        self.state_adapter = self.adapter_factory.get_or_create_adapter(
            self.dev_name, AdapterType.BASE
        )

    def On(self):
        print("Invoking On command on HelperStateDevice")
        return self.state_adapter.On()


@pytest.mark.temp
def test_command_timeout():
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None),
        logger=logger,
        _liveliness_probe=LivelinessProbeType.NONE,
        _event_receiver=False,
    )
    command = StateDevice(
        "dummy/monitored/device", cm, logger, HelperAdapterFactory()
    )
    command.On()
