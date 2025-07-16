from ....automaton.core_interfaces.guard_abc import GuardABC

class DummyGuard(GuardABC):
    """
    a simple guard which will always return true
    """

    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)

        return True