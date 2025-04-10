"""Common Aggregator class for state"""

import logging
from enum import Enum

LOGGER = logging.getLogger(__name__)


class StateAggregator:
    """Generic State Aggregator class for enums like ObsState or HealthState"""

    def __init__(self, state_enum: type[Enum], state_rules: dict):
        """
        :param state_enum: Enum class (e.g., ObsState, HealthState)
        :param state_rules: Rules to use for aggregation
        :type state_enum: Enum meta class
        :type state_rules: dict
        """
        self.state_enum = state_enum
        self.state_rules = state_rules

    def aggregate(self, event_data: dict) -> Enum:
        """
        Aggregate state based on event data

        :param event_data: event data dict required for aggregation
        :type event_data: dict
        :return: Aggregated enum value
        :rtype: Enum
        :raises ValueError: Raise error if invalid enum is present
        """
        LOGGER.debug("Got event data for aggregation %s", event_data)
        for state_name, state_rules in self.state_rules.items():
            LOGGER.debug("Checking rules for state %s", state_name)
            if any(rule.matches(event_data) for rule in state_rules):
                return (
                    self.state_enum[state_name]
                    if hasattr(self.state_enum, state_name)
                    else state_name
                )
        raise ValueError("No matching state found for given event data")
