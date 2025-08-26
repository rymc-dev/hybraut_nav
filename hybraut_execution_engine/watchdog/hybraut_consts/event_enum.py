#!/usr/bin/python3
# -*- coding: utf-8  -*-
""" 
Enum class for pythonic representation 
of the ros2 interface for events for the 
FSM as defined in `hybraut_interfaces.msg.AutomatonEvents
"""

from enum import Enum
from hybraut_interfaces.msg import AutomatonEvents

class EventEnum(Enum):
    """ === System Initialization Events === """
    ACTIVATE_MISSION = AutomatonEvents.ACTIVATE_MISSION
    
    """ === Transition Events ==="""
    ENABLE_GUARD = AutomatonEvents.ENABLE_GUARD
    COMPLETE_TRANSITION = AutomatonEvents.COMPLETE_TRANSITION
    
    """ === Error and Recovery Events ==="""
    COMPLETE_RECOVERY = AutomatonEvents.COMPLETE_RECOVERY
    FAIL_RECOVERY = AutomatonEvents.FAIL_RECOVERY   
    CRITICAL_FAILURE = AutomatonEvents.CRITICAL_FAILURE
    SHUTDOWN_SYSTEM = AutomatonEvents.SHUTDOWN_SYSTEM
    
    """ === Mission Termination Events === """
    FINISH_MISSION = AutomatonEvents.FINISH_MISSION
    DEACTIVATE_MISSION = AutomatonEvents.DEACTIVATE_MISSION
    
    """ === Exception Events === """
    RECOVERABLE_EXCEPTION = AutomatonEvents.RECOVERABLE_EXCEPTION
    UNRECOVERABLE_EXCEPTION = AutomatonEvents.UNRECOVERABLE_EXCEPTION