# Resets

This module contains the [resets file](./resets.py). In this file you can implement your own custom reset functions which will update 
the states in your hybrid automaton environment. 

Once these resets have been written you simply need to give the name of the function in the hybrid automaton config like so: 

```python
from sample_state_interface.msg import AgentState
from geometry_msgs.msg import Point

def reset_state_variable(agent_state:AgentState) -> AgentState:
    """A simple AgentState reset function"""
    return AgentState(position=Point(x=agent_state.position.x + 1, y=agent_state.position.y + 1))
```