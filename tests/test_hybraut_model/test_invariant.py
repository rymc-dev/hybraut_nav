from hybraut_model.invariants import InvariantWrapper, InvariantRegistry
from hybraut_model.automaton_types import ComponentPath
from hybraut_aci import IOSpec, IOSpec, InvariantInterface
import pytest
from builtin_interfaces.msg import Time
from typing import Dict, Any


@pytest.mark.fixture
def sample_invariant_aci_instance() -> InvariantInterface:
    """hello world"""

    class SampleInvariant(InvariantInterface):
        """simple invariant for testing"""

        _init_input_spec = [IOSpec.create_io_spec("true_or_false", bool)]
        _state_input_spec = [IOSpec.create_io_spec("time", Time)]

        def _evaluate(self, **state_kwargs):
            print(
                state_kwargs.get(
                    "time", "Exception occured retrieving state_kwargs time"
                )
            )
            return self.__getattribute__("true_or_false", None)

    return SampleInvariant


class TestInvariantWrapper:
    @classmethod
    def load_invariant_from_amdl(
        cls, invariant_name: str, invariant_dict: Dict[str, Any]
    ) -> InvariantWrapper:
        component_path = ComponentPath.load_component_from_famd(invariant_dict)
        component_class = component_path.get_component_class()
        configuration = invariant_dict.get("configuration", {})

        return cls(
            _name=invariant_name,
            _component_class=component_class,
            _configuration=configuration,
        )

    def test_invariant_wrapper_initialization(self, sample_invariant_aci_instance):
        """Test the initialization of InvariantWrapper with a sample ACI instance."""
        invariant_wrapper = InvariantWrapper(
            _name="sample",
            _component_class=sample_invariant_aci_instance,
            _configuration={"true_or_false": True},
        )
        print(invariant_wrapper)
        print(repr(invariant_wrapper))


if __name__ == "__main__":
    TestInvariantWrapper().test_invariant_wrapper_initialization(
        sample_invariant_aci_instance()
    )


class TestInvariantRegistry:
    pass
