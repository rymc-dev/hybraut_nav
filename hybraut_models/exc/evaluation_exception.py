class EvaluationException(Exception):
    """
    Raised for errors during evaluation in the Hybraut model.

    Attributes:
        message: Human-readable description of the error.
        expression: Optional expression or context related to the error.
    """

    def __init__(self, message: str, expression: str | None = None):
        super().__init__(message)
        self.expression = expression