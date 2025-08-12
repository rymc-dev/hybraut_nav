class NoneStateError(Exception):
    """
    Exception raised when a state is expected but not found.
    This is used to indicate that a required state is missing
    in the evaluation context.
    """

    def __init__(self, state_name: str):
        super().__init__(f"State '{state_name}' is not defined or has no value.")
        self.state_name = state_name
