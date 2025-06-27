from .invariant import Invariant

class FailingInvariant(Invariant):
    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)
        return False