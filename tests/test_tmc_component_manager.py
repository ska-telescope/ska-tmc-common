import logging

from ska_tmc_common.op_state_model import TMCOpStateModel
from tests.helpers.helper_tmc_device import DummyComponentManager

logger = logging.getLogger(__name__)


def test_set_data():
    op_state_model = TMCOpStateModel(logger)
    cm = DummyComponentManager(op_state_model, logger)
    cm.set_data("New value")
    assert cm.sample_data == "New value"
