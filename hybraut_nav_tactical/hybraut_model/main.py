
from .core import TransitionRegistry

""" === Main function for testing or running the module, not for production use === """


def main():
    # Example usage of Transition and TransitionrRegistry

    transition_data = {
        "transition_1": {
            "target_mode": 2,
            "guard": ["guard_1", "guard_2"],
            "reset": ["reset_1"],
            "urgency": 1,  # EAGER urgency,
        },
        "transition_2": {
            "target_mode": 3,
            "guard": ["guard_3"],
            "reset": ["reset_2", "reset_3"],
            "urgency": 2,  # LAZY urgency
        },
    }

    transition_registry = TransitionRegistry()


    print(f"string transition_registry representation: {transition_registry}\n")
    print(f"__repr__ transition_registry representation: {repr(transition_registry)}")


if __name__ == "__main__":
    main()