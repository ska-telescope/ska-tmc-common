import json

from ska_tango_base import SKABaseDevice
from tango.server import attribute, device_property


class TMCBaseDevice(SKABaseDevice):
    """
    Class for common attributes.
    """

    # -----------------
    # Device Properties
    # -----------------
    SleepTime = device_property(dtype="DevFloat", default_value=1)

    # -----------------
    # Attributes
    # -----------------

    @attribute(
        dtype="DevString",
        doc="commandInProgress attribute of TMC Nodes .",
    )
    def commandInProgress(self):
        if not issubclass(TMCBaseDevice, self.__class__):
            return self.component_manager.command_executor.command_in_progress

    @attribute(
        dtype=(("DevString",),),
        max_dim_x=4,
        max_dim_y=1000,
    )
    def commandExecuted(self):
        """Return the commandExecuted attribute."""
        result = []
        for command_executed in reversed(
            self.component_manager.command_executor.command_executed
        ):
            single_res = [
                str(command_executed["Id"]),
                str(command_executed["Command"]),
                str(command_executed["ResultCode"]),
                str(command_executed["Message"]),
            ]
            result.append(single_res)
        return result

    @attribute(
        dtype="DevString",
        doc="Json String representing the last device info changed in the internal model.",
    )
    def lastDeviceInfoChanged(self):
        return self.last_device_info_changed

    @attribute(
        dtype="DevString",
        doc="Last command executed as string: uniqueid, command name, .result and message",
    )
    def lastCommandExecuted(self):
        """Return the lastCommandExecuted attribute as list of string."""
        command_executed = (
            self.component_manager.command_executor.command_executed[-1]
        )
        single_res = "{0} {1} {2} {3}".format(
            str(command_executed["Id"]),
            str(command_executed["Command"]),
            str(command_executed["ResultCode"]),
            str(command_executed["Message"]),
        )
        return single_res

    @attribute(
        dtype="DevString",
        doc="Json String representing the entire internal model transformed for better reading.",
    )
    def transformedInternalModel(self):
        return self.transformedInternalModel_read()

    def transformedInternalModel_read(self):
        """
        This method consists of basic  read implementation of transformedInternalModel and
        must be overloaded to add additional values to result dictionary.
        Returns json string with device data.

        Sample Output:
        {'mccs':{'state':'DevState.UNKNOWN','healthState':'HealthState.UNKNOWN','ping':'-1','last_event_arrived':'None','unresponsive':'False','exception':'None','id':-1,'pointingState':'PointingState.NONE'}}

        """
        json_model = json.loads(self.component_manager.component.to_json())
        result = {}
        if (
            "TmcLeafNodeComponentManager"
            not in self.component_manager.__class__.__bases__
        ):
            for dev in json_model["devices"]:
                dev_name = dev["dev_name"]
                del dev["dev_name"]
                result[dev_name] = dev
        else:
            dev = json_model["device"]
            dev_name = dev["dev_name"]
            del dev["dev_name"]
            result[dev_name] = dev
        return json.dumps(result)

    @attribute(
        dtype="DevString",
        doc="Json String representing the entire internal model.",
    )
    def internalModel(self):
        return self.internalModel_read()

    def internalModel_read(self):
        """
            This method consists of basic  read implementation of InternalModel and
            must be overloaded to add additional attribute values to internal model.
            Returns json string representing internal model with basic attributes only.

        Sample Output:
        {"subarray_health_state":"HealthState.UNKNOWN","devices":[{"dev_name":"mccs","state":"DevState.UNKNOWN","healthState":"HealthState.UNKNOWN","ping":"-1","last_event_arrived":"None","unresponsive":"False","exception":"None","id":-1,"pointingState":"PointingState.NONE"}]}
        """
        return self.component_manager.component.to_json()
