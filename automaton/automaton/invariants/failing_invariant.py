from automaton.invariants import InvariantABC

class FailingInvariant(InvariantABC):
    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)
        return False
    
if __name__ == '__main__':
    invariant: InvariantABC = FailingInvariant()
    invariant_output: bool = invariant.__call__()

    print (invariant_output)