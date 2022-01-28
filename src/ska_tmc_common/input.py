class InputParameter:
    def __init__(self, changed_callback) -> None:
        self._changed_callback = changed_callback

    def update(self, component_manager):
        raise NotImplementedError("This class must be inherited!")
