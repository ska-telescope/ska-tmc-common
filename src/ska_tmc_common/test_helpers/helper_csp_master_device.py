"""
This module defines a helper device that acts as csp master in our testing.
"""

# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
import json
import threading
import time
from typing import List, Tuple

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import AdminMode
from ska_telmodel.data import TMData
from tango import DevState
from tango.server import AttrWriteType, attribute, command, run

from ska_tmc_common import DevFactory
from ska_tmc_common.admin_mode_decorator import admin_mode_check
from ska_tmc_common.test_helpers.constants import (
    CSP_SUBARRAY_DEVICE_LOW,
    CSP_SUBARRAY_DEVICE_MID,
)
from ska_tmc_common.test_helpers.empty_component_manager import (
    EmptyComponentManager,
)
from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


# pylint: disable=invalid-name
class HelperCspMasterDevice(HelperBaseDevice):
    """A helper device class for Csp Controller device"""

    def init_device(self) -> None:
        super().init_device()
        self._source_dish_vcc_config: str = ""
        self._dish_vcc_config: str = ""
        self._admin_mode: AdminMode = AdminMode.OFFLINE
        self.dev_name = self.get_name()

    sourceDishVccConfig = attribute(
        dtype="DevString", access=AttrWriteType.READ
    )
    adminMode = attribute(
        dtype=AdminMode,
        access=AttrWriteType.READ_WRITE,
        label="Admin Mode",
        doc="Admin mode of the device.",
    )
    dishVccConfig = attribute(dtype="DevString", access=AttrWriteType.READ)

    class InitCommand(HelperBaseDevice.InitCommand):
        """A class for the HelperCspMasterDevice's init_device() command."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            :return: ResultCode and message
            """
            super().do()
            self._device.set_change_event("sourceDishVccConfig", True, False)
            self._device.set_change_event("dishVccConfig", True, False)
            return (ResultCode.OK, "")

    def create_component_manager(self) -> EmptyComponentManager:
        """
        Creates an instance of EmptyComponentManager
        :return: component manager instance
        :rtype: EmptyComponentManager
        """
        empty_component_manager = EmptyComponentManager(
            logger=self.logger,
            communication_state_callback=None,
            component_state_callback=None,
        )
        return empty_component_manager

    def read_adminMode(self) -> AdminMode:
        """
        This method reads the adminMode value of the device.
        :return: admin_mode value
        :rtype: AdminMode
        """
        return self._admin_mode

    # New write method for adminMode
    def write_adminMode(self, value: AdminMode) -> None:
        """
        This method writes the adminMode value of the device.
        """
        if value not in [
            AdminMode.ONLINE,
            AdminMode.OFFLINE,
            AdminMode.ENGINEERING,
        ]:
            self.logger.error(
                "Invalid adminMode value. Allowed values are"
                + "'ONLINE','OFFLINE','ENGINEERING'."
            )
            return

        if self._admin_mode != value:
            self._admin_mode = value

            try:
                if "low" in self.dev_name:
                    csp_subarray_device_name = CSP_SUBARRAY_DEVICE_LOW
                else:
                    csp_subarray_device_name = CSP_SUBARRAY_DEVICE_MID

                dev_factory = DevFactory()
                csp_subarray_proxy = dev_factory.get_device(
                    csp_subarray_device_name
                )
                csp_subarray_proxy.adminMode = value

            except Exception as e:
                self.logger.error(
                    "Failed to set adminMode for device %s. Error: %s",
                    csp_subarray_device_name,
                    str(e),
                )
            self.logger.info("AdminMode set to %s", self._admin_mode)
            self.push_change_event("adminMode", self._admin_mode)

    def read_sourceDishVccConfig(self) -> str:
        """
        This method reads the sourceDishVccConfig value of the dish.
        :return: source_dish_vcc_config value
        :rtype:str
        """
        return self._source_dish_vcc_config

    def read_dishVccConfig(self) -> str:
        """
        This method reads the dishVccConfig value of the dish.
        :return: dish_vcc_config value
        :rtype:str
        """
        return self._dish_vcc_config

    @admin_mode_check()
    def is_On_allowed(self) -> bool:
        """
        This method checks if the On command is allowed
        in current state.
        :return: ``True`` if the command is allowed
        :rtype: bool
        """
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self, argin: list) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes On command on CSP Master
        :return: ResultCode and message
        :rtype: Tuple
        """
        command_id = f"{time.time()}_On"
        self.logger.info("Instructed simulator to invoke On command")

        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault("On", command_id)
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
            self.push_change_event("State", self.dev_state())
            self.logger.info("On command completed.")
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_Off_allowed(self) -> bool:
        """
        This method checks if the Off command is allowed
        in current state.
        :return: ``True`` if the command is allowed
        :rtype: bool
        """
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self, argin: list) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Off command on CSP Master
        :return: ResultCode and message
        :rtype: Tuple
        """
        command_id = f"{time.time()}_Off"
        self.logger.info("Instructed simulator to invoke Off command")

        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault("Off", command_id)
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)
            self.push_change_event("State", self.dev_state())
            self.logger.info("Off command completed.")
        return [ResultCode.QUEUED], [command_id]

    @admin_mode_check()
    def is_Standby_allowed(self) -> bool:
        """
        This method checks if the Standby command is allowed
        in current state.
        :return: ``True`` if the command is allowed
        :rtype: bool
        """
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self, argin: list) -> Tuple[List[ResultCode], List[str]]:
        """
        This method invokes Standby command on CSP Master
        :return: ResultCode and message
        :rtype: Tuple
        """
        command_id = f"{time.time()}_Standby"

        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault("Standby", command_id)
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
            self.push_change_event("State", self.dev_state())
            self.logger.info("Standby command completed.")
        return [ResultCode.QUEUED], [command_id]

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ResetSysParams(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This Command Reset Sys Param and source sys param
        :return: ResultCode and message
        """
        self._source_dish_vcc_config = ""
        self._dish_vcc_config = ""
        return [ResultCode.OK], [""]

    @admin_mode_check()
    def is_LoadDishCfg_allowed(self) -> bool:
        """
        This method checks if the LoadDishCfg command is allowed
        in current state.
        :return: ``True`` if the command is allowed
        :rtype: bool
        """
        return True

    def push_dish_vcc_config_and_source_dish_vcc_config(self):
        """Push sys param and source sys param event"""
        self.push_change_event(
            "sourceDishVccConfig", self._source_dish_vcc_config
        )
        self.push_change_event("dishVccConfig", self._dish_vcc_config)
        self.logger.info(
            "Pushed dishVccConfig and sourceDishVccConfig event with values: "
            + "%s, %s",
            self._source_dish_vcc_config,
            self._dish_vcc_config,
        )

    @command(
        dtype_in="str",
        doc_in="The string in JSON format.\
        The JSON contains following values: data source,path and interface",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def LoadDishCfg(self, argin: str) -> Tuple[List[ResultCode], List[str]]:
        """
        This command updates attribute sourceDishVccConfig and dishVccConfig

        :param argin: json with File URI.
        :dtype: str
        :return: ResultCode and message
        :rtype: Tuple

        Example argin:
        {
        "interface":
        "https://schema.skao.int/ska-mid-cbf-initial-parameters/2.2",

        "tm_data_sources": [tm_data_sources]
        #The data source that is used to store the data
        and is accessible through the Telescope Model

        "tm_data_filepath": "path/to/file.json"
        #The path to the json file containing the Mid.CBF initialization
        parameters within the data source

        }
        """
        command_id = f"{time.time()}_LoadDishCfg"
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault("LoadDishCfg", command_id)

        json_argument = json.loads(argin)
        sources = json_argument["tm_data_sources"]
        filepath = json_argument["tm_data_filepath"]
        self.logger.debug(
            "Received source:%s and file path:%s", sources, filepath
        )
        mid_cbf_initial_parameters = TMData(sources)[filepath].get_dict()
        mid_cbf_initial_parameters_str = json.dumps(mid_cbf_initial_parameters)
        self.logger.debug(
            "Updating sourceDishVccConfig attribute with:%s"
            + "and dishVccConfig attribute with:%s",
            argin,
            mid_cbf_initial_parameters_str,
        )
        self._source_dish_vcc_config = argin
        self._dish_vcc_config = mid_cbf_initial_parameters_str

        push_dish_vcc_config_thread = threading.Timer(
            self._delay, self.push_dish_vcc_config_and_source_dish_vcc_config
        )
        push_dish_vcc_config_thread.start()

        # Provided additional 1 sec delay to push
        # command result after sys param event pushed
        push_command_result_thread = threading.Timer(
            self._delay + 1,
            self.push_command_result,
            args=[
                ResultCode.OK,
                "LoadDishCfg",
            ],
            kwargs={"message": "command LoadDishCfg completed"},
        )
        push_command_result_thread.start()
        return [ResultCode.QUEUED], [command_id]


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the HelperCspMasterDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((HelperCspMasterDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
