class StateTimeoutException(Exception):
    """
    Raised when a state evaluation exceeds the allowed timeout.

    Attributes:
        state_name: Name of the state that timed out.
    """

    def __init__(self, state_name: str):
        message = f"State '{state_name}' timed out."  # <-- single space
        super().__init__(message)
        self.state_name = state_name
