import pytest
from unittest.mock import patch
from hybraut_nav_strategy import StrategyNode
from hybraut_nav.state import NodeState

class MockParameter:
    def __init__(self, value):
        self.value = value

@pytest.fixture
def strategy_node():
    return object.__new__(StrategyNode)

""" === getter tests === """

@pytest.mark.parametrize("method,expected", [
    ("get_planner_type", "A*"),
    ("get_description", "sample description of the class"),
])
def test_strategy_node_get_methods(strategy_node: StrategyNode, method, expected):
    with patch.object(strategy_node, "get_parameter", return_value=MockParameter(expected)):
        assert getattr(strategy_node, method)() == expected

@pytest.mark.parametrize("expected_state", [
    (NodeState.ACTIVE),
    (NodeState.INACTIVE)
])
def test_strategy_node_get_state(strategy_node: StrategyNode, expected_state: NodeState):
    strategy_node._state = expected_state
    assert strategy_node.get_state() == expected_state

""" === setter tests === """

def test_set_state_valid(strategy_node: StrategyNode):
    strategy_node.set_state(NodeState.ACTIVE)
    assert strategy_node.get_state() == NodeState.ACTIVE

def test_set_state_rejects_non_node_state(strategy_node: StrategyNode):
    with pytest.raises(Exception):
        strategy_node.set_state("active")

def test_is_active(strategy_node: StrategyNode):
    strategy_node._state = NodeState.INACTIVE
    assert not strategy_node.is_active()
    strategy_node._state = NodeState.ACTIVE
    assert strategy_node.is_active()

if __name__ == '__main__':
    pytest.main([__file__])
