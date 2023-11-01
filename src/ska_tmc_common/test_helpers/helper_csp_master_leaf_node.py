"""
This module defines a helper device that acts as csp master in our testing.
"""


# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
import json
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
        self._source_sys_param: str = ""
        self._sys_param: str = ""

    sourceSysParam = attribute(dtype="DevString", access=AttrWriteType.READ)
    sysParam = attribute(dtype="DevString", access=AttrWriteType.READ)

    class InitCommand(HelperBaseDevice.InitCommand):
        """A class for the HelperCspMasterDevice's init_device() command."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.
            """
            super().do()
            self._device.set_change_event("sourceSysParam", True, False)
            self._device.set_change_event("sysParam", True, False)
            return (ResultCode.OK, "")

    def read_sourceSysParam(self) -> str:
        """
        This method reads the sourceSysParam value of the dish.
        :rtype:str
        """
        return self._source_sys_param

    def read_sysParam(self) -> str:
        """
        This method reads the sysParam value of the dish.
        :rtype:str
        """
        return self._sys_param

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def ResetSysParams(self) -> Tuple[List[ResultCode], List[str]]:
        """This Command Reset sysParam and sourceSysParam attribute"""
        self._source_sys_param = ""
        self._sys_param = ""
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
        This command updates attribute sourceSysParam and sysParam
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
        self.logger.debug(
            "Received source:%s and file path:%s", sources, filepath
        )
        mid_cbf_initial_parameters = TMData(sources)[filepath].get_dict()
        mid_cbf_initial_parameters_str = json.dumps(mid_cbf_initial_parameters)
        self.logger.debug(
            "Updating sourceSysParam attribute with:%s"
            + "and sysParam attribute with:%s",
            argin,
            mid_cbf_initial_parameters_str,
        )
        self._source_sys_param = argin
        self._sys_param = mid_cbf_initial_parameters_str
        self.push_change_event("sourceSysParam", self._source_sys_param)
        self.push_change_event("sysParam", self._sys_param)

        self.push_command_result(ResultCode.OK, "LoadDishCfg")
        return [ResultCode.QUEUED], [""]


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
