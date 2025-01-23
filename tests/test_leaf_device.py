from tango import DevState
from tango.server import command, run

from ska_tmc_common.test_helpers.empty_component_manager import (
    EmptyComponentManager,
)
from ska_tmc_common.tmc_base_leaf_device import TMCBaseLeafDevice


class TestLeafDevice(TMCBaseLeafDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_change_event("state", True)
        self.set_archive_event("state", True)

    def create_component_manager(self) -> EmptyComponentManager:
        """
        Creates an instance of EmptyComponentManager
        :return: component manager instance
        :rtype: EmptyComponentManager
        """
        empty_component_manager = EmptyComponentManager(
            logger=self.logger,
            communication_state_callback=None,
            component_state_callback=None,
        )
        return empty_component_manager

    @command(dtype_in=DevState)
    def push_state_event(self, argin):
        self.push_change_archive_events("state", argin)


def main(args=None, **kwargs):
    """
    Runs the TestLeafDevice Tango device.
    :param args: Arguments internal to TANGO

    :param kwargs: Arguments internal to TANGO

    :return: integer. Exit code of the run method.
    """
    return run((TestLeafDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
