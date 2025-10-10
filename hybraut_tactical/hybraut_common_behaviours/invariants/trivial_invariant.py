from hybraut_aci import InvariantInterface


class TrivialInvariant(InvariantInterface):
    def _evaluate(self, **state_kwargs) -> bool:
        return True


def main():
    invariant: InvariantInterface = TrivialInvariant()
    result: bool = invariant()

    print(f"Trivial Invariant Test Result: {result}")


if __name__ == "__main__":
    main()
