import sys
import os

# Add path two directories back
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import rclpy
from rclpy.node import Node
from colav_interfaces.srv import UpdateDynamics
from scripts.dynamics import (
    dynamics_CRUISE,
    dynamics_T2Theta,
    dynamics_T2LOS,
    dynamics_FB,
    dynamics_WAYPOINT_REACHED
)

class DynamicsNode(Node):
    
    _MODES = {  # dict showing the name of the control modes.
        1: "CRUISE",
        2: "T2LOS",
        3: "T2Theta",
        4: "FB",
        5: "WAYPOINT_REACHED"
    }

    _DYNAMICS = {
        _MODES[1]: dynamics_CRUISE,
        _MODES[2]: dynamics_T2LOS,
        _MODES[3]: dynamics_T2Theta,
        _MODES[4]: dynamics_FB,
        _MODES[5]: dynamics_WAYPOINT_REACHED
    }

    def __init__(
        self,
        namespace:str = "hybrid_automaton",
        name: str = "dynamics"
    ):
        super().__init__(name, namespace=namespace)
        self.create_service(
            'update_dynamics',
             UpdateDynamics,
             self._update_dynamics
        )

    def _update_dynamics(self, request: UpdateDynamics.Request, response: UpdateDynamics.Response):
        """updating dynamics"""
        try:
            if self._DYNAMICS[request.mode] is not None:
                pass 
        except Exception as e:
            response._success = False
            response._success_message = str(e)
            response._mode_num = 0

        return response

def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = DynamicsNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print (f'Exception occured: {str(e)}')

    rclpy.shutdown()

if __name__ == '__main__':
    main()