"""Test aggregation process"""

import enum
import time
from dataclasses import dataclass
from datetime import datetime
from multiprocessing import Event, Manager, Queue

from ska_control_model import ObsState

from ska_tmc_common.v1.aggregate_process import AggregationProcess


@dataclass
class ObsStateData:
    """Test ObsState data."""

    obs_state: enum.IntEnum
    event_timestamp: datetime


@dataclass
class EventDataStorage:
    """Event data storage class."""

    command_in_progress: str
    obs_state_data: dict


class DummyAggregator:
    """Dummy aggregator class."""

    def aggregate(self, event_dict):
        """Aggregate method for dummy aggregator."""
        obsstate_dict = event_dict["event_data"]["obs_state_data"]
        first_obsstate = next(iter(obsstate_dict.values()))["obs_state"]
        return {"obsstate": ObsState(first_obsstate).name}


class DummyAggregationProcess(AggregationProcess):
    """Aggregation process methods."""

    def _convert_event_data_to_dict_for_rule_engine(self, event_data):
        """Return empty dict."""
        return {}

    def set_state_aggregator(self):
        """Return dummy aggregator."""
        return DummyAggregator()


def test_aggregation_process_updates_state_correctly():
    """Test the aggregation process."""
    manager = Manager()
    aggregated_state = manager.list([{}])
    event_queue = Queue()
    update_event = Event()

    process = DummyAggregationProcess(
        event_data_queue=event_queue,
        aggregated_state=aggregated_state,
        update_event=update_event,
    )

    process.start_aggregation_process()

    test_event_data = EventDataStorage(
        command_in_progress="AssignResources",
        obs_state_data={
            "csp/1": ObsStateData(
                obs_state=ObsState.IDLE, event_timestamp=datetime.now()
            )
        },
    )

    event_queue.put(test_event_data)

    update_event.wait(timeout=2)
    time.sleep(0.5)

    process.stop_aggregation_process()

    assert aggregated_state[0] == {"obsstate": "IDLE"}
