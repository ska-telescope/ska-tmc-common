import logging

import pytest

from ska_tmc_common.op_state_model import TMCOpStateModel
from ska_tmc_common.test_helpers.helper_tmc_device import DummyComponent
from ska_tmc_common.tmc_component_manager import TmcComponentManager

logger = logging.getLogger(__name__)


def test_add_device():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    cm.add_device("dummy/monitored/device")
    cm.add_device("dummy/subarray/device")

    assert len(dummy_component._devices) == 2


def test_get_device():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    cm.add_device("dummy/monitored/device")

    dummy_device_info = cm.get_device("dummy/monitored/device")
    assert dummy_device_info.dev_name == "dummy/monitored/device"


def test_update_device():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    cm.add_device("dummy/monitored/device")
    device_info = cm.get_device("dummy/monitored/device")
    assert device_info.unresponsive is False

    device_info._unresponsive = True
    cm.update_device_info(device_info)
    new_device_info = cm.get_device("dummy/monitored/device")
    assert new_device_info.unresponsive is True


def test_telescope_on():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    # raise NotImplementedError
    with pytest.raises(NotImplementedError):
        cm.telescope_on()


def test_telescope_off():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    # raise NotImplementedError
    with pytest.raises(NotImplementedError):
        cm.telescope_off()


def test_telescope_standby():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    # raise NotImplementedError
    with pytest.raises(NotImplementedError):
        cm.telescope_standby()


def test_assign_resources():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    # raise NotImplementedError
    with pytest.raises(NotImplementedError):
        cm.assign_resources()


def test_release_resources():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    # raise NotImplementedError
    with pytest.raises(NotImplementedError):
        cm.release_resources()


def test_check_if_command_is_allowed():
    op_state_model = TMCOpStateModel(logger)
    dummy_component = DummyComponent(logger)
    cm = TmcComponentManager(op_state_model, dummy_component, logger)
    # raise NotImplementedError
    with pytest.raises(NotImplementedError):
        cm.check_if_command_is_allowed()
