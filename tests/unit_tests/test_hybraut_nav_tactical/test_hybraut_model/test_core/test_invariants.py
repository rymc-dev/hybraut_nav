from hybraut_models.core.invariants import InvariantWrapper, InvariantRegistry
from hybraut_models.ldr import ComponentPath
from hybraut_aci import IOSpec, InvariantInterface
from builtin_interfaces.msg import Time
import pytest
from typing import Dict, Any
from hybraut_interfaces.msg import InvariantEvaluationMSG


# --- Mock Invariant for testing ---
class SampleInvariant(InvariantInterface):
    _init_input_spec = [IOSpec.create_io_spec("true_or_false", bool)]
    _state_input_spec = [IOSpec.create_io_spec("time", Time)]

    def _evaluate(self, **state_kwargs):
        return getattr(self, "true_or_false", True)


@pytest.fixture
def sample_invariant_aci_instance():
    return SampleInvariant  # return the class


# --- Tests for InvariantWrapper ---
class TestInvariantWrapper:
    @classmethod
    def load_invariant_from_amdl(
        cls, invariant_name: str, invariant_dict: Dict[str, Any]
    ) -> InvariantWrapper:
        component_path = ComponentPath.load_component_from_famd(invariant_dict)
        component_class = component_path.get_component_class()
        configuration = invariant_dict.get("configuration", {})

        return cls(
            name=invariant_name,
            component_class=component_class,
            configuration=configuration,
        )

    def test_invariant_wrapper_initialization(self, sample_invariant_aci_instance):
        wrapper = InvariantWrapper(
            name="sample",
            component_class=sample_invariant_aci_instance,
            configuration={"true_or_false": True},
        )
        assert wrapper.name == "sample"
        assert wrapper.is_initialized
        assert wrapper.component_instance.true_or_false is True

    def test_invariant_wrapper_evaluate_success(self, sample_invariant_aci_instance):
        wrapper = InvariantWrapper(
            name="sample",
            component_class=sample_invariant_aci_instance,
            configuration={"true_or_false": True},
        )

        class DummyContext:
            def get_state_values(self, state_names):
                return {"time": Time(sec=1, nanosec=0)}

        context = DummyContext()
        result = wrapper._evaluate(context)
        assert isinstance(result, InvariantEvaluationMSG)
        assert result.holds == True
        assert result.error == False
        assert result.message == ""

    def test_invariant_wrapper_evaluate_not_initialized(
        self, sample_invariant_aci_instance
    ):
        wrapper = InvariantWrapper(
            name="sample",
            component_class=sample_invariant_aci_instance,
            configuration={"true_or_false": True},
        )
        wrapper.is_initialized = False
        wrapper.component_instance = None

        class DummyContext:
            def get_state_values(self, state_names):
                return {"time": Time(sec=0, nanosec=0)}

        context = DummyContext()
        with pytest.raises(RuntimeError):
            wrapper._evaluate(context)

    def test_invariant_wrapper_evaluate_component_exception(
        self, sample_invariant_aci_instance
    ):
        class FailingInvariant(sample_invariant_aci_instance):
            def _evaluate(self, **kwargs):
                raise ValueError("fail!")

        wrapper = InvariantWrapper(
            name="failing",
            component_class=FailingInvariant,
            configuration={"true_or_false": True},
        )

        class DummyContext:
            def get_state_values(self, state_names):
                return {"time": Time(sec=0, nanosec=0)}

        context = DummyContext()
        msg = wrapper._evaluate(context)
        assert msg.error
        assert "exception occured during invariant evaluation" in msg.message.lower()


# # --- Tests for InvariantRegistry ---
# class TestInvariantRegistry:
#     def setup_method(self):
#         self.registry = InvariantRegistry()
#         self.registry._components = {}

#         # Add a dummy invariant
#         wrapper = InvariantWrapper(
#             name="dummy",
#             component_class=sample_invariant_aci_instance,
#             configuration={"true_or_false": True},
#         )
#         self.registry._components["dummy"] = wrapper

#     def test_get_num_invariants(self):
#         assert self.registry.get_num_invariants() == 1

#     def test_get_invariant_names(self):
#         names = self.registry.get_invariant_names()
#         assert names == ["dummy"]

#     def test_get_invariant_by_name(self):
#         invariant = self.registry.get_invariant_by_name("dummy")
#         assert isinstance(invariant, InvariantWrapper)
#         assert invariant._name == "dummy"
#         # Non-existent returns None
#         assert self.registry.get_invariant_by_name("nonexistent") is None

#     def test_evaluate_invariant_by_name_success(self):
#         class DummyContext:
#             def get_state_values(self, state_names):
#                 return {"time": Time(sec=0, nanosec=0)}

#         context = DummyContext()
#         msg = self.registry.evaluate_invariant_by_name("dummy", context)
#         assert not msg.error
#         assert msg.invariant_name == "dummy"
#         assert msg.invariant_evaluation is True

#     def test_evaluate_invariant_by_name_failure(self):
#         class FailingInvariant(sample_invariant_aci_instance):
#             def _evaluate(self, **kwargs):
#                 raise ValueError("fail!")

#         self.registry._components["dummy"]._component_instance = FailingInvariant()

#         class DummyContext:
#             def get_state_values(self, state_names):
#                 return {"time": Time(sec=0, nanosec=0)}

#         context = DummyContext()
#         msg = self.registry.evaluate_invariant_by_name("dummy", context)
#         assert msg.error
#         assert "exception occured during invariant evaluation" in msg.message.lower()


if __name__ == "__main__":
    pytest.main([__file__])
