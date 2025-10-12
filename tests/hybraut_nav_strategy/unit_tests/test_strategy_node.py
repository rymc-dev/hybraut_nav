import pytest
from unittest.mock import patch
from hybraut_nav_strategy import StrategyNode
from hybraut_nav_strategy.strategy_node import StrategyState

class MockParameter:
    def __init__(self, value):
        self.value = value

@pytest.fixture
def strategy_node():
    return object.__new__(StrategyNode)

""" === getter tests === """

@pytest.mark.parametrize("method,expected", [
    ("get_replan_frequency", 0.5),
    ("get_planner_type", "rrt*"),
    ("get_max_planning_time", 0.5),
    ("get_description", "sample description of the class"),
])
def test_strategy_node_get_methods(strategy_node: StrategyNode, method, expected):
    with patch.object(strategy_node, "get_parameter", return_value=MockParameter(expected)):
        assert getattr(strategy_node, method)() == expected

@pytest.mark.parametrize("expected_state", [
    (StrategyState.ACTIVE),
    (StrategyState.INACTIVE)
])
def test_strategy_node_get_state(strategy_node: StrategyNode, expected_state: StrategyState): 
    setattr(strategy_node, 'state', expected_state)
    assert strategy_node.get_state() == expected_state

""" === setter tests === """

def test_set_planner_valid_path_string(self):
    """ 
    
    """
    pass

def test_set_planner_valid_path_plannertype(self):
    pass


if __name__ == '__main__':
    pytest.main([__file__])
