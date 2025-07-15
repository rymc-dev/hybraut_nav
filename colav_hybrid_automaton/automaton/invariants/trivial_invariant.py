from automaton.invariants import InvariantABC

class TrivialInvariant(InvariantABC):
    def __call__(self, **state_kwargs):
        super.__call__(**state_kwargs)
        return True
    
    
if __name__ == '__main__':
    invariant: InvariantABC = TrivialInvariant()
    invariant_output: bool = invariant.__call__()

    print (invariant_output)