class StateTimeoutException(Exception):
    """
    Exception raised when a state evaluation exceeds the allowed timeout.
    """

    def __init__(self, state_name: str):
        super().__init__(f"State '{state_name}'  timed out.")
        self.state_name = state_name
