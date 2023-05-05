from typing import Callable, Optional


class InputParameter:
    def __init__(self, changed_callback: Optional[Callable]) -> None:
        self._changed_callback = changed_callback

    def update(self, component_manager) -> NotImplementedError:
        raise NotImplementedError("This class must be inherited!")
