from hybraut_aci import GuardInterface, IOSpec
from std_msgs.msg import Bool


class BooleanFlagGuard(GuardInterface):
    _init_input_spec = [IOSpec.create_io_spec("expected_flag", bool)]
    _state_input_spec = [IOSpec.create_io_spec("flag_msg", Bool)]

    def _evaluate(self, **state_kwargs) -> bool:
        flag_msg: Bool = state_kwargs["flag_msg"]
        return flag_msg.data == self.expected_flag


def main():
    flag = Bool()
    flag.data = True

    flag_guard = BooleanFlagGuard(expected_flag=True)
    result = flag_guard(flag_msg=flag)
    print(f"BooleanFlagGuard result: {result}")


if __name__ == "__main__":
    main()
