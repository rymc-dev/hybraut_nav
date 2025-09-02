#!/usr/bin/python3
# -*- coding: utf-8  -*-
""" 
Enum clas for pythonic representation 
of the ROS2 Interface Enums for the FSM 
defined in `hybraut_interfaces.msg.AutomatonStatus"
"""

from enum import Enum
from hybraut_interfaces.msg import State


class StateEnum(Enum):
    """ 
    watchdog FSM formal definition for states is:
    
    Q = (qo, q1, q2, q3, q4, q5, q6) 
    
    where: 
        qo = INACTIVE
        q1 = ACTIVE
        q2 = TRANSITIONING
        q3 = ERROR
        q4 = RECOVERING
        q5 = FATAL
        q6 = MISSION_COMPLETE
    """
    
    """ === Initialization and Idle States"""
    INACTIVE=State.INACTIVE                 # q0
    
    """ === Operation States === """
    ACTIVE=State.ACTIVE                     # q1
    TRANSITIONING=State.TRANSITIONING       # q2
    
    """ === Health Monitoring States === """
    ERROR=State.ERROR                       # q3
    RECOVERING=State.RECOVERING             # q4
    SYSTEM_SHUTDOWN=State.SYSTEM_SHUTDOWN   # q7

    """ === Terminal States === """
    FATAL=State.FATAL                       # q5
    MISSION_COMPLETE=State.MISSION_COMPLETE # q6