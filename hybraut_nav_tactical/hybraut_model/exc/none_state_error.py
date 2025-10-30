class NoneStateError(Exception):
    """
    Raised when a required state is missing in the evaluation context.

    Attributes:
        state_name: Name of the missing state.
    """

    def __init__(self, state_name: str):
        message = f"State '{state_name}' is not defined or has no value."
        super().__init__(message)
        self.state_name = state_name