import os
import sys

sys.path.append(os.path.dirname(__file__))

import numpy as np
from hybrid_automaton_sim import HybridAutomaton, HybridState, HybridTransition, IntegrationMethod

class TB3Hybrid(HybridAutomaton):
    
    # Define states
    move_forward = HybridState(
        "MoveForward", 
        flow=lambda state: np.array([0.0, 0.0, 0.0]),  # No change in heading
        integration_method=IntegrationMethod.EULER
    )
    
    avoid_obstacle = HybridState(
        "AvoidObstacle",
        flow=lambda state: np.array([0.0, 0.0, 0.5]),  # Turn at 0.5 rad/s
        integration_method=IntegrationMethod.EULER
    )
    
    # Define transitions
    to_avoid = move_forward.to(avoid_obstacle)
    to_forward = avoid_obstacle.to(move_forward)
    
    def __init__(self):
        super().__init__()
        
        # Continuous state: [x, y, theta]
        self.continuous_state = np.array([0.0, 0.0, 0.0])
        
        # Map events to HybridTransition objects
        self.transitions_map = {
            "to_avoid": HybridTransition(
                guard=lambda state: self.detect_obstacle(),  # obstacle detected
                reset=None,
                priority=1
            ),
            "to_forward": HybridTransition(
                guard=lambda state: not self.detect_obstacle(),  # path clear
                reset=None,
                priority=0
            )
        }
    
    def detect_obstacle(self):
        """
        Dummy obstacle detection function.
        Replace this with your real sensor data (e.g., LIDAR)
        """
        # Example: obstacle if x > 2.0
        x, y, theta = self.continuous_state
        return x > 2.0
    
    # Override property
    @property
    def continuous_state(self):
        return self._state
    
    @continuous_state.setter
    def continuous_state(self, value):
        self._state = value