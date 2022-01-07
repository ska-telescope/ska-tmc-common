from ska_tango_base.commands import BaseCommand, ResultCode


class CommandNotAllowed(Exception):
    """Raised when a command is not allowed."""


class TMCCommand(BaseCommand):
    def __init__(self, target, *args, logger=None, **kwargs):
        super().__init__(target, args, logger, kwargs)
        print(logger)

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
