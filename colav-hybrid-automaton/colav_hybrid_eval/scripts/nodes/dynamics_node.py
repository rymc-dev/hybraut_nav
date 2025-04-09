from rclpy.node import Node

class DynamicsNode(Node):
    def __init__(
        self,
        namespace:str = "hybrid_automaton",
        name: str = "dynamics"
    ):
        super().__init__(name, namespace=namespace)
        self.create_service(
            'update_dynamics'
---