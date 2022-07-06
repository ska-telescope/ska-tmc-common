import logging

from ska_tmc_common.monitoring_loop import MonitoringLoop
from ska_tmc_common.tmc_component_manager import TmcComponentManager

logger = logging.getLogger(__name__)


def test_stop():
    cm = TmcComponentManager(logger=logger)
    mm = MonitoringLoop(cm, logger)
    mm.start()
    assert mm._thread.is_alive()

    mm.stop()
    assert mm._stop


def test_add_priority_devices():
    cm = TmcComponentManager(logger=logger)
    mm = MonitoringLoop(cm, logger)
    initial_size = mm._priority_devices._qsize()
    mm.add_priority_devices("dummy/monitored/device")

    assert mm._priority_devices._qsize() == initial_size + 1
