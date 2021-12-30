# from tests.settings import logger
# from ska_tmc_common.op_state_model import TMCOpStateModel
# from ska_tmc_common.tmc_component_manager import TmcComponentManager
# from tests.helpers.helper_tmc_device import DummyComponent, DummyTmcDevice
# import pytest
# from ska_tango_base.base import SKABaseDevice

# @pytest.fixture(scope="module")
# def devices_to_load():
#     return (
#         {
#             "class": DummyTmcDevice,
#             "devices": [
#                 {"name": "dummy/tmc/device"},
#             ],
#         },
#         {
#             "class": SKABaseDevice,
#             "devices": [
#                 {"name": "dummy/monitored/device"}
#             ]
#         }
#     )

# def test_event_receiver(tango_context_multitest):
#     op_state_model = TMCOpStateModel(logger)
#     dummy_component = DummyComponent(logger)
#     cm = TmcComponentManager(op_state_model, dummy_component, logger)
#     cm.add_device("dummy/monitored/device")
#     # dev_info = cm.get_device("dummy/test/device")
#     # cm._event_receiver.subscribe_events(dev_info)
