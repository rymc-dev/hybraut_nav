#!/usr/bin/python3
"""
"""
from rclpy.node import Node
from utils.resets import (
    reset_CRUISE_to_T2LOS,
    reset_WAYPOINT_REACHED_to_CRUISE
)
from colav_interfaces.srv import Reset

class HAResetsNode(Node):

    _RESETS = {
        'WAYPOINT_REACHED_to_CRUISE': reset_WAYPOINT_REACHED_to_CRUISE,
        'CRUISE_to_T2LOS': reset_CRUISE_to_T2LOS
    }

    def __init__(
        self,
        name: str = 'resets_node',
        namespace: str = 'hybrid_automaton'
    ):
        super().__init__(name, namespace=namespace)

        self.create_service(
            srv_type=Reset(),
            srv_name='reset',
            callback=self._reset_callback
        )

    def _reset_callback(self, request: Reset.Request, response: Reset.Response):
        """
        """
        try:
            reset_name = request._reset_name
            if reset_name in list(self._RESETS.keys()):
                response.reset_name = reset_name
                reset_func = self._RESETS[f"reset_{reset_name}"]
                reset_func() 
                response._success = True
                response._message = f"Reset successfully applied"
            else:
                response._success = False
                response._message = f"Reset transition name does not exist: {str(reset_name)}"
        except Exception as e:
            self.get_logger().error(f'Error occured during reset_callback: {str(e)}')
            response._success = False
            response._message = f"{str(e)}"

        return response
        