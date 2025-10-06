# import pytest
# from hybraut_execution_engine.watchdog.hybraut_consts import TransitionEventEnum
# from hybraut_interfaces.msg import TransitionEvent

# def test_transition_event_enum_values():
#     assert TransitionEventEnum.ACTIVATE_MISSION.value == TransitionEvent.ACTIVATE_MISSION
#     assert TransitionEventEnum.ENABLE_GUARD.value == TransitionEvent.ENABLE_GUARD
#     assert TransitionEventEnum.COMPLETE_TRANSITION.value == TransitionEvent.COMPLETE_TRANSITION
#     assert TransitionEventEnum.COMPLETE_RECOVERY.value == TransitionEvent.COMPLETE_RECOVERY
#     assert TransitionEventEnum.FAIL_RECOVERY.value == TransitionEvent.FAIL_RECOVERY
#     assert TransitionEventEnum.CRITICAL_FAILURE.value == TransitionEvent.CRITICAL_FAILURE
#     assert TransitionEventEnum.SHUTDOWN_SYSTEM.value == TransitionEvent.SHUTDOWN_SYSTEM
#     assert TransitionEventEnum.FINISH_MISSION.value == TransitionEvent.FINISH_MISSION
#     assert TransitionEventEnum.DEACTIVATE_MISSION.value == TransitionEvent.DEACTIVATE_MISSION
#     assert TransitionEventEnum.RECOVERABLE_EXCEPTION.value == TransitionEvent.RECOVERABLE_EXCEPTION
#     assert TransitionEventEnum.UNRECOVERABLE_EXCEPTION.value == TransitionEvent.UNRECOVERABLE_EXCEPTION
#     assert TransitionEventEnum.ATTEMPT_RECOVERY.value == TransitionEvent.ATTEMPT
    
    
# if __name__ == '__main__':
#     pytest.main()