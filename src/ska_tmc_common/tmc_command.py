from ska_tango_base.commands import BaseCommand, ResultCode

# from tango import DevState


# from ska_tmc_common.adapters import AdapterFactory, AdapterType
# from ska_tmc_centralnode.model.input import InputParameterMid


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
        # component_manager = self.target

        # if isinstance(component_manager.input_parameter, InputParameterMid):
        #     result = self.check_allowed_mid()
        # else:
        #     result = self.check_allowed_low()

        # return result

    def init_adapters(self):
        raise NotImplementedError("This class must be inherited!")
        # component_manager = self.target

        # if isinstance(component_manager.input_parameter, InputParameterMid):
        #     result, message = self.init_adapters_mid()
        # else:
        #     result, message = self.init_adapters_low()

        # return result, message

    def do(self, argin=None):
        raise NotImplementedError("This class must be inherited!")
        # component_manager = self.target

        # if isinstance(component_manager.input_parameter, InputParameterMid):
        #     result = self.do_mid(argin)
        # else:
        #     result = self.do_low(argin)

        # return result

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
