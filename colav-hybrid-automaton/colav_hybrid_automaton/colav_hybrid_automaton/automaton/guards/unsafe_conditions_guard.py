from .guard import Guard

class UnsafeConditionsGuard(Guard):
    """
    
    # TODO: TO be implemented
    """

    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)
        # dummy guard, currently just returns False always.
        return False