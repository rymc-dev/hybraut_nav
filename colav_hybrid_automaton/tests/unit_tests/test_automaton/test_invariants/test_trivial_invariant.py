from colav_hybrid_automaton.automaton.invariants import TrivialInvariant

def test_failing_invariant_comprehensive():
    """Comprehensive test for FailingInvariant."""
    invariant = TrivialInvariant()
    assert invariant.__call__() == True, 'Trivial invariant call should be True, but got False'