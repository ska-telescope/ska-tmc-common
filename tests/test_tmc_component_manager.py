import logging

from ska_tmc_common.op_state_model import TMCOpStateModel
from ska_tmc_common.tmc_component_manager import TmcComponentManager

# from tests.helpers.helper_tmc_device import (
#     DummyComponent,
#     DummyComponentManager,
# )
from tests.helpers.helper_tmc_device import DummyComponent

logger = logging.getLogger(__name__)


# def test_set_data():
#     op_state_model = TMCOpStateModel(logger)
#     cm = DummyComponentManager(op_state_model, logger)
#     cm.set_data("New value")
#     assert cm.sample_data == "New value"


def test_get_device():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    cm.add_device("dummy/monitored/device")
    cm.add_device("dummy/subarray/device")
    # dummy_device_info = None
    dummy_device_info = cm.get_device("dummy/monitored/device")
    assert dummy_device_info.dev_name == "dummy/monitored/device"
    dummy_device_info = cm.get_device("dummy/subarray/device")
    assert dummy_device_info.dev_name == "dummy/subarray/device"
