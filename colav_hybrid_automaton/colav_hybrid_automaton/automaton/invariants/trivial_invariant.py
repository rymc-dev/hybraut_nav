from .invariant import Invariant

class TrivialInvariant(Invariant):
    def __call__(self, **state_kwargs):
        super.__call__(**state_kwargs)
        return True