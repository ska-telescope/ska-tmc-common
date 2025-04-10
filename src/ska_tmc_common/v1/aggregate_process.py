"""
This module contain process for aggregation
"""

import logging
import queue
from dataclasses import asdict
from multiprocessing import Event, Process, Queue
from typing import Any, Callable, Dict, Optional

LOGGER = logging.getLogger(__name__)


class AggregationProcess:
    """
    Generic Aggregation Process Class

    This class handles multiprocessing-based event queue consumption
    and uses a passed-in aggregator and data converter to perform aggregation.
    """

    def __init__(
        self,
        event_data_queue: Queue,
        aggregated_state: list,
        update_event: Event,
        state_aggregator: Any,
        event_data_converter: Callable[[Any], Dict],
        callback: Optional[Callable[[Any], None]] = None,
    ):
        """
        :param event_data_queue: Queue to track event data
        :type event_data_queue: multiprocessing queue
        :param aggregated_state: Aggregated state updated after
            aggregation this is shared variable between process
        :type aggregated_state: list
        :param callback: Callback method reference used when aggregated
            state is updated
        """
        self.event_data_queue = event_data_queue
        self.aggregated_state = aggregated_state
        self.aggregate_update_event = update_event
        self.state_aggregator = state_aggregator
        self.event_data_converter = event_data_converter
        self.callback = callback

        self.aggregation_process = Process(
            target=self._run_process, name="aggregation_process"
        )
        self.alive_event = Event()

    def _run_process(self):
        """This process run when subarray node start
        and check if any data receive in queue then get
        data from queue and call aggregate method
        """
        LOGGER.info(
            "Aggregation process started with PID %s",
            self.aggregation_process.pid,
        )
        while not self.alive_event.is_set():
            try:
                event_data = self.event_data_queue.get(timeout=0.1)
                event_dict = self.event_data_converter(event_data)
                event_dict["event_data"] = asdict(event_data)

                self.aggregated_state[0] = self.state_aggregator.aggregate(
                    event_dict
                )
                self.aggregate_update_event.set()

                if self.callback:
                    self.callback(self.aggregated_state[0])

                LOGGER.debug("Aggregated state: %s", self.aggregated_state[0])
            except queue.Empty:
                continue

    def start(self):
        """Start the aggregation process"""
        self.aggregation_process.start()

    def stop(self):
        """Stop the aggregation process"""
        LOGGER.debug("Stopping aggregation process")
        if self.aggregation_process.is_alive():
            self.alive_event.set()
            self.aggregation_process.join()
        LOGGER.debug("Aggregation process stopped")

    def _convert_event_data_to_dict_for_rule_engine(self, event_data):
        """Override this method in child classes
        :param event_data: Event data object contain data required for
            aggregation
        :type event_data: EventDataStorage
        :raises NotImplementedError: Imeplementation not present
        """
        raise NotImplementedError
