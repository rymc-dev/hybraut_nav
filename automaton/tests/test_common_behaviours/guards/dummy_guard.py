from ....automaton_models.hybrid.aci_interfaces.guard_interface import GuardABC

class DummyGuard(GuardABC):
    """
    a simple guard which will always return true
    """

    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)

        return True