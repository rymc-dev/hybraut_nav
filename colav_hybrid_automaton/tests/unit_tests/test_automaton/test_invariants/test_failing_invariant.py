from colav_hybrid_automaton.automaton.invariants import FailingInvariant

def test_failing_invariant_comprehensive():
    """Comprehensive test for FailingInvariant."""
    invariant = FailingInvariant()
    assert invariant.__call__() == False, 'Failing invariant call should be false, but got true'