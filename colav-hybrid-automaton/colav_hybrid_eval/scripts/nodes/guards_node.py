import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult, ParameterType
import os
from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate
from colav_interfaces.srv import EvaluateTransitions

class HAGuardsNode(Node):
    def __init__(
        self,
        namespace:str = "hybrid_automaton",
        name:str = "guards"
    ):
        super().__init__(name, namespace=namespace)

        # Initialisation functions
        self._NODE_SUBS = self._init_node_subs()
        self._NODE_SRVS = self._init_node_srvs()

    def _init_node_srvs(self):
        """initialize the nodes services"""
        try:
            return {
                "evalute_transitions": self.create_service(
                    srv_type=EvaluateTransitions,
                    srv_name="/evaluate_transitions",
                    callback=self._evaluate_transitions
                )
            }
        except Exception as e:
            self.get_logger().error(f"{self.__class__}::init_node_srvs: Exception occured: {str(e)}")
            raise e
        
    def _evaluate_transitions(self, request: EvaluateTransitions.Request, response: EvaluateTransitions.Response):
        """evalute the transitions passed in"""
        try:
            pass
        except Exception as e:
            self.get_logger(f"{self.__class__}::_evaluate_transitions: Exception occured: {str(e)}")
            response.overall_success = False
            response.message = str(e)
        
        return response

    def _init_node_subs(self):
        try:
            return {
                "agent_update": self.create_subscription(

                ),
                "obstacles_update": self.create_subscription(

                )
            }
        except Exception as e:
            self.get_logger().error(str(e))
            raise e

def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = HAGuardsNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
