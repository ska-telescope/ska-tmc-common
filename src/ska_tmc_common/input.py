"""
Module has abstract methods for different nodes
"""

from typing import Callable, Optional


class InputParameter:
    """
    Base class for update method for different nodes
    """

    def __init__(self, changed_callback: Optional[Callable]) -> None:
        self._changed_callback = changed_callback

    def update(self, component_manager) -> NotImplementedError:
        """
        Base method for update method for different nodes
        :raises NotImplementedError: Not implemented error
        """
        raise NotImplementedError("This class must be inherited!")
