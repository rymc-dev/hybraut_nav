#!/usr/bin/python3
# -*- coding: utf-8  -*-
""" 
Enum clas for pythonic representation 
of the ROS2 Interface Enums for the FSM 
defined in `hybraut_interfaces.msg.AutomatonStatus"
"""

from enum import Enum
from hybraut_interfaces.msg import AutomatonStatus


class StatusEnum(Enum):
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
    INACTIVE=AutomatonStatus.INACTIVE                 # q0
    
    """ === Operation States === """
    ACTIVE=AutomatonStatus.ACTIVE                     # q1
    TRANSITIONING=AutomatonStatus.TRANSITIONING       # q2
    
    """ === Health Monitoring States === """
    ERROR=AutomatonStatus.ERROR                       # q3
    RECOVERING=AutomatonStatus.RECOVERING             # q4

    """ === Terminal States === """
    FATAL=AutomatonStatus.FATAL                       # q5
    MISSION_COMPLETE=AutomatonStatus.MISSION_COMPLETE # q6