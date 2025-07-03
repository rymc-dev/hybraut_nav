from .invariant import InvariantABC

class FailingInvariant(InvariantABC):
    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)
        return False