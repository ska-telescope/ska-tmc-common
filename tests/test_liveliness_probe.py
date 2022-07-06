import logging

from ska_tmc_common.liveliness_probe import LivelinessProbe
from ska_tmc_common.tmc_component_manager import TmcComponentManager

logger = logging.getLogger(__name__)


def test_stop():
    cm = TmcComponentManager(logger=logger)
    lp = LivelinessProbe(cm, logger)
    lp.start()
    assert lp._thread.is_alive()

    lp.stop()
    assert lp._stop


def test_add_priority_devices():
    cm = TmcComponentManager(logger=logger)
    lp = LivelinessProbe(cm, logger)
    initial_size = lp._priority_devices._qsize()
    lp.add_priority_devices("dummy/monitored/device")

    assert lp._priority_devices._qsize() == initial_size + 1
