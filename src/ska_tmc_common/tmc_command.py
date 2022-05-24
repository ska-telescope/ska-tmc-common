from operator import methodcaller

from ska_tango_base.commands import BaseCommand, ResultCode


class CommandNotAllowed(Exception):
    """Raised when a command is not allowed."""


class TMCCommand(BaseCommand):
    def __init__(self, target, *args, logger=None, **kwargs):
        super().__init__(target, args, logger, kwargs)

    def generate_command_result(self, result_code, message):
        if result_code == ResultCode.FAILED:
            self.logger.error(message)
        self.logger.info(message)
        return (result_code, message)

    def adapter_error_message_result(self, dev_name, e):
        message = f"Error in creating adapter for {dev_name}: {e}"
        self.logger.error(message)
        return ResultCode.FAILED, message

    def check_allowed(self):
        raise NotImplementedError("This class must be inherited!")

    def init_adapters(self):
        raise NotImplementedError("This class must be inherited!")

    def do(self, argin=None):
        raise NotImplementedError("This class must be inherited!")

    def check_allowed_mid(self):
        raise NotImplementedError("This class must be inherited!")

    def check_allowed_low(self):
        raise NotImplementedError("This class must be inherited!")

    def init_adapters_mid(self):
        raise NotImplementedError("This class must be inherited!")

    def init_adapters_low(self):
        raise NotImplementedError("This class must be inherited!")

    def do_mid(self, argin=None):
        raise NotImplementedError("This class must be inherited!")

    def do_low(self, argin=None):
        raise NotImplementedError("This class must be inherited!")


class TmcLeafNodeCommand(BaseCommand):
    def __init__(self, target, *args, logger=None, **kwargs):
        super().__init__(target, *args, logger=logger, **kwargs)

    def generate_command_result(self, result_code, message):
        if result_code == ResultCode.FAILED:
            self.logger.error(message)
        self.logger.info(message)
        return (result_code, message)

    def adapter_error_message_result(self, dev_name, e):
        message = f"Error in creating adapter for {dev_name}: {e}"
        self.logger.error(message)
        return ResultCode.FAILED, message

    def call_adapter_method(self, device, adapter, command_name, *args):
        for value in args:
            argin = value

        self.logger.info(
            f"Invoking {command_name} command on: {adapter.dev_name}"
        )
        try:
            if argin:
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

    def check_allowed(self):
        raise NotImplementedError("This class must be inherited!")

    def init_adapter(self):
        raise NotImplementedError("This class must be inherited!")

    def do(self, argin=None):
        raise NotImplementedError("This class must be inherited!")
