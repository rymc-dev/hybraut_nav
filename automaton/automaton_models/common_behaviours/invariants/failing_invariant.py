from automaton_models.hybrid.aci_interfaces import InvariantInterface


class FailingInvariant(InvariantInterface):
    def _evaluate(self, **state_kwargs) -> bool:
        return False


def main():
    invariant: InvariantInterface = FailingInvariant()
    result: bool = invariant()

    print(f"FailingInvariant Test Result: {result}")

if __name__ == '__main__':
    main()