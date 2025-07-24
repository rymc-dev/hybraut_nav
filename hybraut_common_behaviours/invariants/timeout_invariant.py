
from automaton_models.hybraut_model.aci_interfaces import InvariantInterface
from automaton.spec import IOSpec
import time
from std_msgs.msg import Float64


class TimeoutInvariant(InvariantInterface):
    _init_input_spec = [
        IOSpec.create_io_spec("timeout_sec", float),
        IOSpec.create_io_spec("entry_time", float),
    ]
    _state_input_spec = [
        IOSpec.create_io_spec("current_time", Float64)
    ]

    def _evaluate(self, **state_kwargs) -> bool:
        current_time: Float64 = state_kwargs["current_time"]._data
        return (current_time - self.entry_time) <= self.timeout_sec


def main():
    # Initialize the invariant with a 5-second timeout and an entry time (e.g., now)
    entry = time.time()
    invariant = TimeoutInvariant(timeout_sec=5.0, entry_time=entry)

    # Simulate current time just after entry
    current = entry + 3.0  # 3 seconds later
    print(f"At t+3 seconds, invariant holds? {invariant(current_time=current)}")

    # Simulate current time after timeout expires
    current = entry + 6.0  # 6 seconds later
    print(f"At t+6 seconds, invariant holds? {invariant(current_time=current)}")


if __name__ == '__main__':
    main()
