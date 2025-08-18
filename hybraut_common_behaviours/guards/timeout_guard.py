from hybraut_aci import GuardInterface, IOSpec
import time


class TimeoutGuard(GuardInterface):
    _init_input_spec = [
        IOSpec.create_io_spec("timeout_sec", float),
        IOSpec.create_io_spec("start_time_sec", float),
    ]
    _state_input_spec = [IOSpec.create_io_spec("current_time_sec", float)]

    def _evaluate(self, **state_kwargs) -> bool:
        current_time: float = state_kwargs["current_time_sec"]
        return (current_time - self.start_time_sec) >= self.timeout_sec


def main():
    timeout_guard = TimeoutGuard(timeout_sec=3.0, start_time_sec=time.time() - 5.0)
    result = timeout_guard(current_time_sec=time.time())
    print(f"TimeoutGuard result: {result}")


if __name__ == "__main__":
    main()
