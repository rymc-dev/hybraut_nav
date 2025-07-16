from typing import List, Dict
from .core_interfaces import InvariantABC
from dataclasses import dataclass
from .states import States


class Invariants: 
    _invariants: List['InvariantWrapper']



@dataclass
class InvariantWrapper:
    """ 
    a wrapper dataclass for an InvariantABC
    abstracts some functionalities for an end user.
    """
    _inst: InvariantABC

    def evaluate_invariant(self, states: States) -> bool:
        """
        Evaluate the invariant using the current states of required inputs.
        
        Parameters:
            states (Dict[str, State]): A dictionary mapping input names to State instances.
        
        Returns:
            bool: True if the invariant holds, False otherwise.
        
        Raises:
            RuntimeError: If the invariant is not initialized.
            KeyError: If required state keys are missing.
            TypeError: If current_state types do not match expected types.
        """
        if not self._inst.is_initialized:
            raise RuntimeError("Tried to evaluate an invariant which is not initialized")

        state_input_keys = self._inst.state_input_spec_names()
        state_input_types = self._inst.state_input_spec_types()  # Expected: Dict[str, type]

        state_kwargs = {}
        for key in state_input_keys:
            if key not in states:
                raise KeyError(f"Missing required state for key: '{key}'")

            value = states[key].current_state
            expected_type = state_input_types.get(key)

            if expected_type is not None and not isinstance(value, expected_type):
                raise TypeError(
                    f"State value for key '{key}' has incorrect type: "
                    f"expected {expected_type.__name__}, got {type(value).__name__}"
                )

            state_kwargs[key] = value

        # Evaluate the invariant with validated inputs
        result = self._inst(**state_kwargs)

        if not isinstance(result, bool):
            raise TypeError(f"Invariant evaluation should return a bool, got {type(result).__name__} instead")

        return result

    def get_invariant_info(self):
        return self._inst.get_invariant_info()

    def __repr__(self):
        return repr(self._inst)
    
    def __str__(self):
        return str(self._inst)

    @classmethod
    def load_invariant_from_famd(cls, data: Dict[str, Any]) -> 'InvariantABC':
        inv_cls = import_class(data['module'], data['class_name'])
        inst: InvariantABC = inv_cls(**data.get('configuration', {}))
        info = inst.get_invariant_info()
        return cls(
            instance=inst,
            description=info.get('description', ''),
            state_inputs=data.get('state_inputs', []),
        )

