import logging

from ska_tmc_common.device_info import DishDeviceInfo
from ska_tmc_common.input import InputParameter
from ska_tmc_common.liveliness_probe import (
    MultiDeviceLivelinessProbe,
    SingleDeviceLivelinessProbe,
)
from ska_tmc_common.tmc_component_manager import (
    TmcComponentManager,
    TmcLeafNodeComponentManager,
)

logger = logging.getLogger(__name__)


def test_stop():
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None), logger=logger
    )
    lp = MultiDeviceLivelinessProbe(cm, logger)
    lp.start()
    assert lp._thread.is_alive()

    lp.stop()
    assert lp._stop


def test_stop_ln():
    cm = TmcLeafNodeComponentManager(logger, True)
    device = DishDeviceInfo("dummy/monitored/device")
    lp = SingleDeviceLivelinessProbe(cm, device, logger)
    lp.start()
    assert lp._thread.is_alive()

    lp.stop()
    assert lp._stop


def test_add_device():
    cm = TmcComponentManager(
        _input_parameter=InputParameter(None), logger=logger
    )
    lp = MultiDeviceLivelinessProbe(cm, logger)
    initial_size = lp._monitoring_devices._qsize()
    lp.add_device("dummy/monitored/device")

    assert lp._monitoring_devices._qsize() == initial_size + 1
