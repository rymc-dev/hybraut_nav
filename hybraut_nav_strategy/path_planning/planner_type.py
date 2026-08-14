from enum import Enum
from .planner import Planner
from .astar import AStar

class PlannerType(Enum):
    """Enumeration for planner algorithm types."""
    ASTAR = 'A*'

    @staticmethod
    def from_string(planner_type_str: str) -> 'PlannerType':
        """
        Convert string to PlannerType enum.

        Args:
            planner_type_str: String representation of planner type

        Returns:
            Corresponding PlannerType enum member

        Raises:
            ValueError: If planner type string is not recognized
        """
        for pt in PlannerType:
            if pt.value == planner_type_str:
                return pt
        raise ValueError(f'Unknown planner type string: {planner_type_str}')

    @staticmethod
    def initialize_planner(planner_type: 'PlannerType') -> Planner:
        """
        Factory method to create planner instance.

        Args:
            planner_type: Type of planner to create

        Returns:
            Initialized planner instance

        Raises:
            ValueError: If planner type is not recognized
        """
        planner_map = {
            PlannerType.ASTAR: AStar,
        }

        planner_class = planner_map.get(planner_type)
        if planner_class is None:
            raise ValueError(f'Unknown planner type: {planner_type}')

        return planner_class()
