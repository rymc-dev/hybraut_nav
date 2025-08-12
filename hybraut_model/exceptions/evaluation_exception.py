class EvaluationException(Exception):
    """
    Custom exception for errors during evaluation in the hybraut model.
    """

    def __init__(self, message, expression=None):
        super().__init__(message)
        self.expression = expression
