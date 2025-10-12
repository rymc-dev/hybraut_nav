#!/usr/bin/python3
# -*- coding: utf-8  -*-
""" 
Enum class for pythonic representation 
of the ros2 interface for events for the 
FSM as defined in `hybraut_interfaces.msg.AutomatonEvents
"""

from enum import Enum
from hybraut_interfaces.msg import TransitionEvent

class TransitionEventEnum(Enum):
    """ 
    watchdog FSM formal definition for language correlates with the 
    events which trigger transitions for the hybrid automaton when in 
    a state `(Q)`
    
    L = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    
    where: 
        0 = ACTIVATE_MISSION
        1 = ENABLE_GUARD
        2 = COMPLETE_TRANSITION
        3 = COMPLETE_RECOVERY
        4 = FAIL_RECOVERY
        5 = CRITICAL_FAILURE
        6 = SHUTDOWN_SYSTEM
        7 = FINISH_MISSION
        8 = DEACTIVATE_MISSION
        9 = RECOVERABLE_EXCEPTION 
        10 = UNRECOVERABLE_EXCEPTION
        11 = ATTEMPT_RECOVERY
    """
    """ === System Initialization Events === """
    ACTIVATE_MISSION = TransitionEvent.ACTIVATE_MISSION
    
    """ === Transition Events ==="""
    ENABLE_GUARD = TransitionEvent.ENABLE_GUARD
    COMPLETE_TRANSITION = TransitionEvent.COMPLETE_TRANSITION
    
    """ === Error and Recovery Events ==="""
    COMPLETE_RECOVERY = TransitionEvent.COMPLETE_RECOVERY
    FAIL_RECOVERY = TransitionEvent.FAIL_RECOVERY   
    CRITICAL_FAILURE = TransitionEvent.CRITICAL_FAILURE
    SHUTDOWN_SYSTEM = TransitionEvent.SHUTDOWN_SYSTEM
    
    """ === Mission Termination Events === """
    FINISH_MISSION = TransitionEvent.FINISH_MISSION
    DEACTIVATE_MISSION = TransitionEvent.DEACTIVATE_MISSION
    
    """ === Exception Events === """
    RECOVERABLE_EXCEPTION = TransitionEvent.RECOVERABLE_EXCEPTION
    UNRECOVERABLE_EXCEPTION = TransitionEvent.UNRECOVERABLE_EXCEPTION
    
    """ === Attempt Recovery === """
    ATTEMPT_RECOVERY = TransitionEvent.ATTEMPT_RECOVERY