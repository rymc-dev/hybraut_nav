from hybraut_models.core.guards import GuardWrapper, GuardRegistry
from hybraut_models.ctx import EvaluationContext
from hybraut_aci import GuardInterface
from hybraut_interfaces.msg import GuardEvaluationMSG
import pytest


# --- Mock classes for testing ---
class DummyGuard(GuardInterface):
    def __init__(self):
        self.called = False

    def get_state_input_spec_names(self):
        return ["x", "y"]

    def get_component_info(self):
        return {"class_name": "DummyGuard"}

    def __call__(self, **kwargs):
        return self._evaluate(**kwargs)

    def _evaluate(self, **state_kwargs):
        self.called = True
        # simple sum example
        return state_kwargs.get("x", 0) + state_kwargs.get("y", 0)



class DummyContext(EvaluationContext):
    def get_state_values(self, state_names):
        return {"x": 1, "y": 2}
    

# -- Tests

class TestGuardWrapper: 
    def test_guardwrapper_evaluate_success(self):
        wrapper = GuardWrapper(_name="dummy", _component_class=DummyGuard, _configuration={})
        wrapper._is_initialized = True
        wrapper._name = "TestGuard"

        context = DummyContext(states=None, current_mode=0, stamp=None, metadata={}, guard_registry=None, reset_registry=None, invariant_registry=None)
        
        msg = wrapper._evaluate(context)
        
        assert isinstance(msg, GuardEvaluationMSG)
        assert msg.guard_name == "DummyGuard"
        assert msg.guard_evaluation == 3  # 1 + 2 from DummyContext
        assert not msg.error

    def test_guardwrapper_evaluate_not_initialized(self):
        wrapper = GuardWrapper(_name="dummy", _component_class=DummyGuard, _configuration={})
        wrapper._component_instance = None
        wrapper._is_initialized = False
        wrapper._name = "TestGuard"
        
        context = DummyContext(states=None, current_mode=0, stamp=None, metadata={}, guard_registry=None, reset_registry=None, invariant_registry=None)
        
        with pytest.raises(RuntimeError):
            wrapper._evaluate(context)

    def test_guardwrapper_evaluate_component_raises_exception(self):
        class FailingGuard(DummyGuard):
            def __call__(self, **kwargs):
                raise ValueError("fail!")

        wrapper = GuardWrapper(_name="dummy_guard", _component_class=FailingGuard, _configuration={})
        wrapper._component_instance = FailingGuard()
        wrapper._is_initialized = True
        wrapper._name = "FailGuard"

        context = DummyContext(states=None, current_mode=0, stamp=None, metadata={}, guard_registry=None, reset_registry=None, invariant_registry=None)
        
        msg = wrapper._evaluate(context)
        assert msg.error
        assert "exception occured during guard evaluation" in msg.message


class TestGuardRegistry:
    def setup_method(self):
        # Setup a fresh registry for each test
        self.registry = GuardRegistry()
        self.registry._components = {}

        # Add a test guard
        self.registry._components["dummy"] = GuardWrapper(
            _name="dummy",
            _component_class=DummyGuard,
            _configuration={}
        )
        self.registry._components["dummy"]._is_initialized = True
        self.registry._components["dummy"]._component_instance = DummyGuard()
        self.registry._components["dummy"]._name = "DummyGuard"

    def test_get_num_guards(self):
        assert self.registry.get_num_guards() == 1

    def test_get_guard_names(self):
        names = self.registry.get_guard_names()
        assert names == ["dummy"]

    def test_get_guard_by_name(self):
        guard = self.registry.get_guard_by_name("dummy")
        assert isinstance(guard, GuardWrapper)
        assert guard._name == "DummyGuard"

        # Non-existent guard returns None
        assert self.registry.get_guard_by_name("nonexistent") is None

    def test_evaluate_guard_by_name_success(self):
        context = DummyContext(states=None, current_mode=0, stamp=None, metadata={}, guard_registry=None, reset_registry=None, invariant_registry=None)
        msg = self.registry.evaluate_guard_by_name("dummy", context)
        assert isinstance(msg, GuardEvaluationMSG)
        assert msg.guard_name == "DummyGuard"
        assert msg.guard_evaluation == 3
        assert not msg.error

    def test_evaluate_guard_by_name_failure(self):
        # Replace component with failing guard
        class FailingGuard(DummyGuard):
            def _evaluate(self, **kwargs):
                raise ValueError("fail!")

        self.registry._components["dummy"]._component_instance = FailingGuard()
        context = DummyContext(states=None, current_mode=0, stamp=None, metadata={}, guard_registry=None, reset_registry=None, invariant_registry=None)

        msg = self.registry.evaluate_guard_by_name("dummy", context)
        assert msg.error
        assert "exception occured during guard evaluation" in msg.message

    def test_evaluate_guards_by_name_multiple(self):
        # Add another dummy guard
        self.registry._components["dummy2"] = GuardWrapper(
            _name="dummy2",
            _component_class=DummyGuard,
            _configuration={}
        )
        self.registry._components["dummy2"]._is_initialized = True
        self.registry._components["dummy2"]._component_instance = DummyGuard()
        self.registry._components["dummy2"]._name = "DummyGuard2"

        context = DummyContext(states=None, current_mode=0, stamp=None, metadata={}, guard_registry=None, reset_registry=None, invariant_registry=None)
        results = self.registry.evaluate_guards_by_name(["dummy", "dummy2"], context)

        assert len(results) == 2
        assert all(isinstance(msg, GuardEvaluationMSG) for msg in results)
        assert results[0].guard_evaluation == 3
        assert results[1].guard_evaluation == 3



if __name__ == "__main__":
    pytest.main([__file__])
