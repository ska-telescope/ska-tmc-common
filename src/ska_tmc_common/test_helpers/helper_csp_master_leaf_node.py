"""
This module defines a helper device that acts as csp master in our testing.
"""


# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
import json
import threading
from typing import List, Tuple

from ska_tango_base.commands import ResultCode
from ska_telmodel.data import TMData
from tango.server import AttrWriteType, attribute, command, run

from ska_tmc_common.test_helpers.helper_base_device import HelperBaseDevice


class HelperCspMasterLeafDevice(HelperBaseDevice):
    """A helper device class for Csp Master Leaf device"""

    def init_device(self) -> None:
        super().init_device()
        self._delay: int = 2
        self._source_dish_vcc_config: str = ""
        self._dish_vcc_config: str = ""
        self._dish_vcc_map_validation_result = ResultCode.STARTED
        self._memorized_dish_vcc_map: str = ""

    sourceDishVccConfig = attribute(
        dtype="DevString", access=AttrWriteType.READ
    )
    dishVccConfig = attribute(dtype="DevString", access=AttrWriteType.READ)

    DishVccMapValidationResult = attribute(
        dtype="str", access=AttrWriteType.READ
    )

    @attribute(
        dtype="DevString",
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        hw_memorized=True,
    )
    def memorizedDishVccMap(self):
        """
        This attribute is used for storing latest dish vcc map version data
        into tango DB.Made this attribute memorized so that when device
        restart then previous set dish vcc map version will be used for loading
        dish vcc config on csp master
        """
        return self._memorized_dish_vcc_map

    @memorizedDishVccMap.write
    def memorizedDishVccMap(self, value: str):
        """Set memorized dish vcc map
        :param value: dish vcc config json string
        :type str
        """
        self._memorized_dish_vcc_map = value

    class InitCommand(HelperBaseDevice.InitCommand):
        """A class for the HelperCspMasterDevice's init_device() command."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            """
            super().do()
            self._device.set_change_event("sourceDishVccConfig", True, False)
            self._device.set_change_event("dishVccConfig", True, False)
            self._device.set_change_event(
                "DishVccMapValidationResult", True, False
            )
            self._device.op_state_model.perform_action("component_on")
            self._device.start_dish_vcc_validation()
            return (ResultCode.OK, "")

    def read_sourceDishVccConfig(self) -> str:
        """
        This method reads the sourceDishVccConfig value of the dish.
        :rtype:str
        """
        return self._source_dish_vcc_config

    def read_dishVccConfig(self) -> str:
        """
        This method reads the dishVccConfig value of the dish.
        :rtype:str
        """
        return self._dish_vcc_config

    def read_DishVccMapValidationResult(self) -> str:
        """
        :rtype: str
        """
        return str(int(self._dish_vcc_map_validation_result))

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ResetSysParams(self) -> Tuple[List[ResultCode], List[str]]:
        """
        This Command Reset dishVccConfig and sourceDishVccConfig attribute"""
        self._source_dish_vcc_config = ""
        self._dish_vcc_config = ""
        return [ResultCode.OK], [""]

    def is_LoadDishCfg_allowed(self) -> bool:
        """
        This method checks if the LoadDishCfg command is allowed
        in current state.

        :rtype: bool
        """
        return True

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
        :rtype: Tuple

        :param argin: json with File URI.
        :dtype: str

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
        if self.defective_params["enabled"]:
            self.logger.info("Device is defective, cannot process command.")
            return self.induce_fault(
                "LoadDishCfg",
            )
        json_argument = json.loads(argin)
        sources = json_argument["tm_data_sources"]
        filepath = json_argument["tm_data_filepath"]
        self.logger.info(
            "Received source:%s and file path:%s", sources, filepath
        )
        mid_cbf_initial_parameters = TMData(sources)[filepath].get_dict()
        mid_cbf_initial_parameters_str = json.dumps(mid_cbf_initial_parameters)
        self.logger.info(
            "Updating sourceDishVccConfig attribute with:%s"
            + "and dishVccConfig attribute with:%s",
            argin,
            mid_cbf_initial_parameters_str,
        )
        self._source_dish_vcc_config = argin
        self._dish_vcc_config = mid_cbf_initial_parameters_str
        self.push_change_event(
            "sourceDishVccConfig", self._source_dish_vcc_config
        )
        self.push_change_event("dishVccConfig", self._dish_vcc_config)

        thread = threading.Timer(
            self._delay,
            self.push_command_result,
            args=[ResultCode.OK, "LoadDishCfg"],
        )
        thread.start()
        self._dish_vcc_map_validation_result = ResultCode.OK
        self.push_change_event(
            "DishVccMapValidationResult",
            str(int(self._dish_vcc_map_validation_result)),
        )
        return [ResultCode.QUEUED], [""]

    @command(
        dtype_in="str",
        doc_in="Set DishVccValidationResult and push event",
    )
    def SetDishVccValidationResult(
        self, result: str
    ) -> Tuple[List[ResultCode], List[str]]:
        """Set DishVccValidationResult and push event for same"""
        self._dish_vcc_map_validation_result = int(result)
        thread = threading.Timer(
            self._delay,
            self.push_change_event,
            args=["DishVccMapValidationResult", result],
        )
        thread.start()
        return [ResultCode.QUEUED], [""]

    def push_dish_vcc_validation_result(self):
        """Push Dish Vcc Validation result event
        If memorized dish vcc already set then push Result Code as OK
        else push result code event as UNKNOWN
        """
        if self._memorized_dish_vcc_map:
            self._dish_vcc_map_validation_result = ResultCode.OK
        else:
            self._dish_vcc_map_validation_result = ResultCode.UNKNOWN

        self.logger.info(
            "Push Dish Vcc Validation Result as %s",
            self._dish_vcc_map_validation_result,
        )
        self.push_change_event(
            "DishVccMapValidationResult",
            str(int(self._dish_vcc_map_validation_result)),
        )

    def start_dish_vcc_validation(self):
        """Push Dish Vcc Validation result after Initialization"""
        start_thread = threading.Timer(5, self.push_dish_vcc_validation_result)
        start_thread.start()


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
    return run((HelperCspMasterLeafDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
