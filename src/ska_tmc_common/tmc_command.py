import logging
import time
from operator import methodcaller
from typing import Optional, Tuple

from ska_tango_base.commands import ResultCode
from tango import ConnectionFailed, DevFailed

from ska_tmc_common.adapters import AdapterType


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

    def adapter_creation_retry(
        self,
        device_name: str,
        adapter_type: AdapterType,
        start_time: float,
        timeout: int,
    ):
        adapter = None
        elapsed_time = 0

        while adapter is None and elapsed_time <= timeout:
            try:
                adapter = self.adapter_factory.get_or_create_adapter(
                    device_name,
                    adapter_type,
                )
                return adapter

            except ConnectionFailed as cf:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    return self.adapter_error_message_result(
                        device_name,
                        cf,
                    )
            except DevFailed as df:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    return self.adapter_error_message_result(
                        device_name,
                        df,
                    )
            except Exception as e:
                return self.adapter_error_message_result(
                    device_name,
                    e,
                )

    def generate_command_result(self, result_code, message):
        if result_code == ResultCode.FAILED:
            self.logger.error(message)
        self.logger.info(message)
        return (result_code, message)

    def adapter_error_message_result(self, dev_name, e):
        message = f"Error in creating adapter for {dev_name}: {e}"
        self.logger.error(message)
        return ResultCode.FAILED, message

    def do(self, argin=None):
        raise NotImplementedError("This method must be inherited!")


class TMCCommand(BaseTMCCommand):
    def init_adapters(self):
        raise NotImplementedError("This method must be inherited!")

    def init_adapters_mid(self):
        raise NotImplementedError("This method must be inherited!")

    def init_adapters_low(self):
        raise NotImplementedError("This method must be inherited!")

    def do_mid(self, argin=None):
        raise NotImplementedError("This method must be inherited!")

    def do_low(self, argin=None):
        raise NotImplementedError("This method must be inherited!")


class TmcLeafNodeCommand(BaseTMCCommand):
    def init_adapter(self):
        raise NotImplementedError("This method must be inherited!")

    def do_mid(self, argin=None):
        raise NotImplementedError("This method must be inherited!")

    def do_low(self, argin=None):
        raise NotImplementedError("This method must be inherited!")

    def init_adapter_mid(self):
        raise NotImplementedError("This method must be inherited!")

    def init_adapter_low(self):
        raise NotImplementedError("This method must be inherited!")

    def call_adapter_method(
        self, device, adapter, command_name, argin=None
    ) -> Tuple[ResultCode, str]:
        if adapter is None:
            return self.adapter_error_message_result(
                device,
                "Adapter is None",
            )

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
