# import pytest
# from hybraut_execution_engine.watchdog.hybraut_consts import StateEnum
# from hybraut_interfaces.msg import State

# def test_state_enum_values():
#     assert StateEnum.INACTIVE.value == State.INACTIVE
#     assert StateEnum.ACTIVE.value == State.ACTIVE
#     assert StateEnum.TRANSITIONING.value == State.TRANSITIONING
#     assert StateEnum.ERROR.value == State.ERROR
#     assert StateEnum.RECOVERING.value == State.RECOVERING
#     assert StateEnum.FATAL.value == State.FATAL
#     assert StateEnum.MISSION_COMPLETE.value == State.MISSION_COMPLETE
#     assert StateEnum.SYSTEM_SHUTDOWN.value == 7 # Explicit Terminal State required for watchdog
    
    
# if __name__ == '__main__':
#     pytest.main([__file__])