import logging
from operator import methodcaller
from typing import Optional

from ska_tango_base.commands import ResultCode


class BaseTMCCommand:
    def __init__(
        self,
        component_manager,
        logger: Optional[logging.Logger] = None,
        *args,
        **kwargs,
    ):
        self.component_manager = component_manager
        self.logger = logger

    def generate_command_result(self, result_code, message):
        if result_code == ResultCode.FAILED:
            self.logger.error(message)
        self.logger.info(message)
        return (result_code, message)

    def adapter_error_message_result(self, dev_name, e):
        message = f"Error in creating adapter for {dev_name}: {e}"
        self.logger.error(message)
        return ResultCode.FAILED, message

    def init_adapters(self):
        raise NotImplementedError("This class must be inherited!")

    def do(self, argin=None):
        raise NotImplementedError("This class must be inherited!")


class TMCCommand(BaseTMCCommand):
    def init_adapters_mid(self):
        raise NotImplementedError("This class must be inherited!")

    def init_adapters_low(self):
        raise NotImplementedError("This class must be inherited!")

    def do_mid(self, argin=None):
        raise NotImplementedError("This class must be inherited!")

    def do_low(self, argin=None):
        raise NotImplementedError("This class must be inherited!")


class TmcLeafNodeCommand(BaseTMCCommand):
    def call_adapter_method(self, device, adapter, command_name, *args):
        if adapter is None:
            return self.adapter_error_message_result(
                device,
                "Adapter is None",
            )

        argin = None
        for value in args:
            argin = value

        self.logger.info(
            f"Invoking {command_name} command on: {adapter.dev_name}"
        )
        try:
            if argin is not None:
                func = methodcaller(command_name, argin)
                func(adapter)
            else:
                func = methodcaller(command_name)
                func(adapter)

        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return self.generate_command_result(
                ResultCode.FAILED,
                f"The invocation of the {command_name} command is failed on "
                f"{device} device {adapter.dev_name}.\n"
                f"Reason: Error in calling the {command_name} command on {device}.\n"
                "The command has NOT been executed.\n"
                "This device will continue with normal operation.",
            )
        self.logger.info(
            f"{command_name} command successfully invoked on:{adapter.dev_name}"
        )
        return (ResultCode.OK, "")
