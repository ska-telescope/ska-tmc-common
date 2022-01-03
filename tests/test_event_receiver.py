import pytest

# from ska_tmc_common.op_state_model import TMCOpStateModel
# from ska_tmc_common.tmc_component_manager import TmcComponentManager
from tests.helpers.helper_state_device import HelperStateDevice
from tests.helpers.helper_tmc_device import DummyTmcDevice

# from tests.settings import logger

# from tests.settings import devices_to_load
# from tests.test_adapters import devices_to_load
# from ska_tango_base.base import SKABaseDevice


@pytest.fixture(scope="module")
def devices_to_load():
    return (
        {
            "class": DummyTmcDevice,
            "devices": [
                {"name": "dummy/tmc/device"},
            ],
        },
        {
            "class": HelperStateDevice,
            "devices": [
                {"name": "helper/device/1"},
                {"name": "helper/device/2"},
            ],
        },
    )


# def test_event_receiver(tango_context_multitest):
#     op_state_model = TMCOpStateModel(logger)
#     dummy_component = DummyComponent(logger)
#     cm = TmcComponentManager(op_state_model, dummy_component, logger)
#     cm.add_device("helper/device/1")
#     cm.add_device("helper/device/2")
#     dev_info = cm.get_device("dummy/test/device")
#     cm._event_receiver.subscribe_events(dev_info)
