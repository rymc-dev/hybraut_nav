from enum import Enum
from .controller import Controller
from .finite_time_controller import FiniteTimeController

class ControllerType(Enum): 
    FINITE_TIME_CONTROLLER = "finite_time_controller"
    
    @staticmethod
    def from_string(controller_type_str: str) -> 'ControllerType':
        """
        Convert string to PlannerType enum.
        
        Args:
            controller_type_str: String representation of ControllerType type
            
        Returns:
            Corresponding PlannerType enum member
            
        Raises:
            ValueError: If planner type string is not recognized
        """
        for pt in ControllerType:
            if pt.value == controller_type_str:
                return pt
        raise ValueError(f'Unknown planner type string: {controller_type_str}')

    @staticmethod
    def initialize_controller(controller_type: 'ControllerType') -> Controller:
        """
        Factory method to create controller instance.

        Args:
            controller_type: Type of controller to create
            
        Returns:
            Initialized controller instance

        Raises:
            ValueError: If planner type is not recognized
        """
        planner_map = {
            ControllerType.FINITE_TIME_CONTROLLER: FiniteTimeController,
        }
        
        planner_class = planner_map.get(controller_type)
        if planner_class is None:
            raise ValueError(f'Unknown controller type: {controller_type}')
        
        return planner_class()
    