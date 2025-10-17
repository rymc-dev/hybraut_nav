from typing import Union
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
    def initialize_controller(controller_type: Union[str, 'ControllerType']) -> Controller:
        """
        Factory method to create controller instance.

        Args:
            controller_type: Type of controller to create (str or ControllerType)
            
        Returns:
            Initialized controller instance

        Raises:
            ValueError: If controller type is not recognized
        """
        # Convert string to ControllerType if necessary
        if isinstance(controller_type, str):
            try:
                controller_type_enum = ControllerType.from_string(controller_type)
            except ValueError:
                raise ValueError(f'Unknown controller type: {controller_type}')
        elif isinstance(controller_type, ControllerType):
            controller_type_enum = controller_type
        else:
            raise ValueError(f'Invalid controller type: {controller_type}')

        planner_map = {
            ControllerType.FINITE_TIME_CONTROLLER: FiniteTimeController,
        }
        
        planner_class = planner_map.get(controller_type_enum)
        if planner_class is None:
            raise ValueError(f'Unknown controller type: {controller_type}')
        
        return planner_class()
    