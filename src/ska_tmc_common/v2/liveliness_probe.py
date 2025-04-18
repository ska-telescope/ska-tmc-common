"""
This module monitors sub devices.
Inherited from liveliness probe functionality
"""

# pylint: disable=duplicate-code
import threading
from logging import Logger
from time import sleep
from typing import List

import tango

from ska_tmc_common.dev_factory import DevFactory
from ska_tmc_common.device_info import DeviceInfo
from ska_tmc_common.log_manager import LogManager


class BaseLivelinessProbe:
    """
    The BaseLivelinessProbe class has the responsibility to monitor the sub
    devices.

    It is inherited for basic liveliness probe functionality.

    TBD: what about scalability? what if we have 1000 devices?
    """

    def __init__(
        self,
        component_manager,
        logger: Logger,
        proxy_timeout: int = 500,
        liveliness_check_period: int = 1,
        max_logging_time: int = 5,
    ):
        self._thread = threading.Thread(target=self.run)
        self._stop = False
        self._logger = logger
        self._thread.daemon = True
        self._component_manager = component_manager
        self._proxy_timeout = proxy_timeout
        self._liveliness_check_period = liveliness_check_period
        self._dev_factory = DevFactory()
        self.log_manager = LogManager(max_logging_time)

    def start(self) -> None:
        """
        Starts the sub devices
        """
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        """
        Stops the sub devices
        """
        self._stop = True

    def run(self) -> NotImplementedError:
        """
        Runs the sub devices
        :raises NotImplementedError:raises not implemented error if the method
        is not defined by child class.
        """
        raise NotImplementedError("This method must be inherited")

    def get_device_and_database(
        self, device_name: str
    ) -> tuple[str, tango.Database]:
        """This method provides device name and database details.

        :param device_name: device_name
        :type device_name: str
        :return: device name and database details
        :rtype: tuple[str,tango.Database]
        """
        if "tango://" in device_name:  # check full trl
            db_name, port = device_name.split("/")[2].split(":")
            db = tango.Database(db_name, port)
            splitted_data = device_name.split("/")
            device_name = "/".join(splitted_data[-3:])
        else:
            db = tango.Database()
        return device_name, db

    # pylint: disable=too-many-branches
    def device_task(self, dev_info: DeviceInfo) -> None:
        """This method checks device state and sets device to responsive
        if the device is reachable and able to respond to the state command.
        If the device is not defined in database/unreachable or unable to
        respond to state command, it sets device as unresponsive.

        :param dev_info: DeviceInfo instance
        :type dev_info: DeviceInfo
        """
        try:
            component_manager = self._component_manager
            update_device_availabiity = (
                component_manager.update_device_availabiity_for_subscription
            )
            exception_message: str = ""
            update_failure = (
                component_manager.update_exception_for_unresponsiveness
            )
            device_name, db = self.get_device_and_database(dev_info.dev_name)
            if not db.get_device_info(device_name).exported:
                if self.log_manager.is_logging_allowed("device_unexported"):
                    self._logger.debug(
                        "Device is not yet exported into the tango database, "
                        + "liveliness probe will retry "
                        + "to connect with device: %s",
                        dev_info.dev_name,
                    )
                if not dev_info.unresponsive:
                    update_failure(
                        dev_info,
                        "Device is not yet exported into the tango database:"
                        f" {dev_info.dev_name}",
                    )
            else:
                proxy = self._dev_factory.get_device(dev_info.dev_name)
                proxy.state()
                if dev_info.unresponsive:
                    component_manager.update_responsiveness_info(
                        dev_info.dev_name
                    )
                    update_device_availabiity(dev_info.dev_name)
        except tango.CommunicationFailed as exception:
            if self.log_manager.is_logging_allowed("communication_failed"):
                self._logger.exception(
                    "Communication Failed on %s: Reason: %s",
                    dev_info.dev_name,
                    str(exception),
                )
                exception_message = (
                    f"Communication Failed on {dev_info.dev_name}: "
                    f"{str(exception)}"
                )
        except tango.ConnectionFailed as connection_failed:
            exception_message = (
                "Connection Failed on %s: %s",
                dev_info.dev_name,
                connection_failed,
            )
            match connection_failed.args[0].reason:
                case "DB_DeviceNotDefined":
                    exception_message = (
                        "Device is not defined in database: "
                        + f"{dev_info.dev_name}"
                    )
                case "API_CantConnectToDevice":
                    exception_message = (
                        "Not able to connect to device: "
                        + f"{dev_info.dev_name}"
                    )
                case "API_CantConnectToDatabase":
                    exception_message = (
                        "Failed to connect to database, "
                        + "please check the database host and port"
                    )

            if self.log_manager.is_logging_allowed("connection_failed"):
                self._logger.exception(
                    "Connection Failed on %s: %s",
                    dev_info.dev_name,
                    connection_failed,
                )
        except tango.DevFailed as exception:
            if self.log_manager.is_logging_allowed("dev_failed"):
                self._logger.exception(
                    "Error on %s: %s", dev_info.dev_name, exception
                )
                exception_message = (
                    f"Unable to reach device {dev_info.dev_name}"
                )
        except BaseException as exception:
            if self.log_manager.is_logging_allowed("base_exception"):
                self._logger.exception(
                    "Error on %s: %s", dev_info.dev_name, exception
                )
                exception_message = (
                    f"Unable to reach device {dev_info.dev_name}"
                )

        if exception_message and dev_info.exception != exception_message:
            update_failure(dev_info, exception_message)


class MultiDeviceLivelinessProbe(BaseLivelinessProbe):
    """A class for monitoring multiple devices"""

    def __init__(
        self,
        component_manager,
        logger: Logger,
        max_workers: int = 5,
        proxy_timeout: int = 500,
        liveliness_check_period: int = 1,
        max_logging_time: int = 5,
    ):
        super().__init__(
            component_manager,
            logger,
            proxy_timeout,
            liveliness_check_period,
            max_logging_time,
        )
        self._max_workers = max_workers
        self._monitoring_devices: List[str] = []

    def add_device(self, dev_name: str) -> None:
        """This method is used to add device in the Queue for monitoring

        :param dev_name: Tango device FQDN.
        :type dev_name: str
        """
        if dev_name in self._monitoring_devices:
            self._logger.debug(
                "The device: %s is already present in the monitoring devices "
                + "list.",
                dev_name,
            )
            return
        self._monitoring_devices.append(dev_name)
        self._logger.debug(
            "Added device: %s to the list of monitoring devices. "
            + "Updated list is: %s",
            dev_name,
            self._monitoring_devices,
        )

    def remove_devices(self, dev_names: List[str]) -> None:
        """Remove the given devices from the monitoring queue.

        :param dev_names: Names of devices in a list that are to be removed
            from the monitoring list
        :type dev_names: `List[str]`
        """
        for dev_name in dev_names:
            try:
                self._monitoring_devices.remove(dev_name)
            except ValueError:
                self._logger.debug(
                    "Device: %s is not present in the list of monitoring "
                    + "devices. Current list is: %s",
                    dev_name,
                    self._monitoring_devices,
                )

    def run(self) -> None:
        """A method to run device in the queue for monitoring"""
        with tango.EnsureOmniThread():
            while not self._stop:
                try:
                    for dev_name in self._monitoring_devices:
                        dev_info = self._component_manager.get_device(dev_name)
                        self.device_task(dev_info)
                except (AttributeError, tango.DevFailed) as exception:
                    self._logger.warning("Exception occured: %s", exception)
                except BaseException as exp_msg:
                    self._logger.warning("Exception occured: %s", exp_msg)
                sleep(self._liveliness_check_period)


class SingleDeviceLivelinessProbe(BaseLivelinessProbe):
    """A class for monitoring a single device"""

    def run(self) -> None:
        """A method to run single device in the Queue for monitoring"""
        with tango.EnsureOmniThread():
            while not self._stop:
                try:
                    dev_info = self._component_manager.get_device()
                except (AttributeError, ValueError) as exception:
                    self._logger.error(
                        "Exception occured while getting device info: %s",
                        exception,
                    )
                except BaseException as exp_msg:
                    self._logger.error(
                        "Exception occured while getting device info: %s",
                        exp_msg,
                    )
                else:
                    try:
                        if dev_info.dev_name is None:
                            continue
                        self.device_task(dev_info)
                    except (AttributeError, tango.DevFailed) as exception:
                        self._logger.error(
                            "Error in submitting the task for %s: %s",
                            dev_info.dev_name,
                            exception,
                        )
                    except BaseException as exp_msg:
                        self._logger.error(
                            "Error in submitting the task for %s: %s",
                            dev_info.dev_name,
                            exp_msg,
                        )
                sleep(self._liveliness_check_period)
