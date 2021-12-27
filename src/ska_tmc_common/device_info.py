import json
import threading

from ska_tango_base.control_model import HealthState, ObsState
from tango import DevState


def dev_state_2_str(value):
    if value == DevState.ON:
        return "DevState.ON"
    elif value == DevState.OFF:
        return "DevState.OFF"
    elif value == DevState.CLOSE:
        return "DevState.CLOSE"
    elif value == DevState.OPEN:
        return "DevState.OPEN"
    elif value == DevState.INSERT:
        return "DevState.INSERT"
    elif value == DevState.EXTRACT:
        return "DevState.EXTRACT"
    elif value == DevState.MOVING:
        return "DevState.MOVING"
    elif value == DevState.STANDBY:
        return "DevState.STANDBY"
    elif value == DevState.FAULT:
        return "DevState.FAULT"
    elif value == DevState.INIT:
        return "DevState.INIT"
    elif value == DevState.RUNNING:
        return "DevState.RUNNING"
    elif value == DevState.ALARM:
        return "DevState.ALARM"
    elif value == DevState.DISABLE:
        return "DevState.DISABLE"
    else:
        return "DevState.UNKNOWN"


class DeviceInfo:
    def __init__(self, dev_name: str, _unresponsive=False):
        self.dev_name = dev_name
        self.state = DevState.UNKNOWN
        self.obsState = ObsState.EMPTY
        self.healthState = HealthState.UNKNOWN
        self.ping = -1
        self.last_event_arrived = None
        self.exception = None
        self._unresponsive = _unresponsive
        self.lock = threading.Lock()

    def from_dev_info(self, devInfo):
        self.dev_name = devInfo.dev_name
        self.state = devInfo.state
        self.healthState = devInfo.healthState
        self.ping = devInfo.ping
        self.last_event_arrived = devInfo.last_event_arrived
        self.lock = devInfo.lock

    def update_unresponsive(self, value, exception=None):
        """
        Set device unresponsive

        :param: value unresponsive boolean
        """
        self._unresponsive = value
        self.exception = exception
        if self._unresponsive:
            self.state = DevState.UNKNOWN
            self.obsState = ObsState.EMPTY
            self.healthState = HealthState.UNKNOWN
            self.ping = -1

    @property
    def unresponsive(self):
        """
        Return whether this device is currently unresponsive.

        :return: whether this device is faulting
        :rtype: bool
        """
        return self._unresponsive

    def __eq__(self, other):
        if isinstance(other, DeviceInfo):
            return self.dev_name == other.dev_name
        else:
            return False

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        result = {
            "dev_name": self.dev_name,
            "state": dev_state_2_str(DevState(self.state)),
            "obsState": str(ObsState(self.obsState)),
            "healthState": str(HealthState(self.healthState)),
            "ping": str(self.ping),
            "last_event_arrived": str(self.last_event_arrived),
            "unresponsive": str(self.unresponsive),
            "exception": str(self.exception),
        }
        return result
