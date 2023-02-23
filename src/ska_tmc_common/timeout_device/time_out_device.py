"""
CSP Master Leaf node acts as a CSP contact point
for Master Node and also to monitor
and issue commands to the CSP Master.
"""
from ska_control_model import HealthState

# pylint: disable=arguments-differ, fixme
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from tango import DebugIt
from tango.server import command, run
from ska_tmc_common.timeout_device.component_manager import TimeOutComponentManager

from ska_tmc_common.adapters import AdapterFactory

__all__ = ["TimeOutDevice", "main"]


class TimeOutDevice(SKABaseDevice):
    """ """

    # -----------------
    # Device Properties
    # -----------------

    # -----------------
    # Attributes
    # -----------------

    # ---------------
    # General methods
    # ---------------

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the TimeOutDevice's init_device() method.
        """

        def do(self):
            """
            Initializes the attributes and properties of the
            TimeOutDevice.

            return:
                A tuple containing a return code and a string message
                indicating status.
                The message is for information purpose only.

            rtype:
                (ResultCode, str)
            """
            super().do()
            device = self._device
            device._health_state = HealthState.OK
            device.set_change_event("healthState", True, False)
            device.op_state_model.perform_action("component_on")
            return (ResultCode.OK, "")

    def always_executed_hook(self):
        pass

    def delete_device(self):
        # if the init is called more than once
        # I need to stop all threads
        if hasattr(self, "component_manager"):
            self.component_manager.stop_event_receiver()
            self.component_manager.stop_liveliness_probe()

    # ------------------
    # Attributes methods
    # ------------------

    # --------
    # Commands
    # --------

    def is_Command_allowed(self):
        """Checks whether this command is allowed"""
        return self.component_manager.is_command_allowed("On")

    # TODO: To support input argument to turn on specific devices.
    @command(
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def Command(self):
        """
        This command invokes Command() command .

        """
        handler = self.get_command_object("Command")
        result_code, unique_id = handler()

        return [[result_code], [unique_id]]

    # default ska mid
    def create_component_manager(self):
        _adapter_factory = AdapterFactory()
        cm = TimeOutComponentManager(
            _adapter_factory=_adapter_factory,
            logger=self.logger,
            _event_receiver=False,
        )
        return cm

    def init_command_objects(self):

        super().init_command_objects()
        for (command_name, method_name) in [
            ("Command", "command"),
        ]:
            self.register_command_object(
                command_name,
                SubmittedSlowCommand(
                    command_name,
                    self._command_tracker,
                    self.component_manager,
                    method_name,
                    logger=self.logger,
                ),
            )


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the TimeOutDevice.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: TimeOutDevice TANGO object.
    """
    return run((TimeOutDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
