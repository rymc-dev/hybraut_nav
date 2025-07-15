from abc import ABC, abstractmethod
from typing import Any, Dict, Type, List, Optional, ClassVar
from dataclasses import dataclass, field
from collections import namedtuple
from rclpy.logging import get_logger
from colav_hybrid_automaton.automaton._internal.types import InputSpec
from collections import deque

@dataclass
class DynamicsField:
    """
    Represents a single field in the dynamics specification.
    
    Args:
        name: Field name (e.g., 'yaw_rate', 'velocity')
        dtype: Python type (e.g., float, int)
        unit: Unit string (e.g., 'rad/s', 'm/s')
        description: Optional description of the field
        default: Optional default value
        bounds: Optional tuple of (min, max) values
    """
    name: str
    dtype: Type
    unit: str
    description: Optional[str] = None
    default: Optional[Any] = None
    bounds: Optional[tuple] = None

    def __post_init__(self):
        """Validate the field specification."""
        if not isinstance(self.name, str) or not self.name.isidentifier():
            raise ValueError(f"Field name '{self.name}' must be a valid Python identifier")
        
        if not isinstance(self.dtype, type):
            raise TypeError(f"dtype must be a type, got {type(self.dtype)}")
        
        if not isinstance(self.unit, str):
            raise TypeError(f"unit must be a string, got {type(self.unit)}")
        
        if self.bounds is not None:
            if not isinstance(self.bounds, tuple) or len(self.bounds) != 2:
                raise ValueError("bounds must be a tuple of (min, max)")
            if self.bounds[0] is not None and self.bounds[1] is not None:
                if self.bounds[0] >= self.bounds[1]:
                    raise ValueError("bounds minimum must be less than maximum")
    
    def validate_value(self, value: Any) -> bool:
        """Validate that a value conforms to this field specification."""
        if value is None and self.default is not None:
            return True
        
        if not isinstance(value, self.dtype):
            return False
        
        if self.bounds is not None:
            min_val, max_val = self.bounds
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
        
        return True
    
    def get_value_or_default(self, value: Any) -> Any:
        """Get the value or default if value is None."""
        return value if value is not None else self.default

@dataclass
class DynamicsSpec:
    """
    Specification for dynamics function inputs/outputs.
    
    This class allows you to define the structure of your dynamics data
    including field names, types, units, and validation rules.
    """
    name: str
    fields: List[DynamicsField] = field(default_factory=list)
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate the specification."""
        if not isinstance(self.name, str) or not self.name.isidentifier():
            raise ValueError(f"Spec name '{self.name}' must be a valid Python identifier")
        
        # Check for duplicate field names
        field_names = [f.name for f in self.fields]
        if len(field_names) != len(set(field_names)):
            raise ValueError("Duplicate field names are not allowed")
    
    def add_field(self, name: str, dtype: Type, unit: str, **kwargs) -> 'DynamicsSpec':
        """
        Add a field to the specification.
        
        Args:
            name: Field name
            dtype: Python type
            unit: Unit string
            **kwargs: Additional field properties (description, default, bounds)
        
        Returns:
            Self for method chaining
        """
        field_obj = DynamicsField(name=name, dtype=dtype, unit=unit, **kwargs)
        self.fields.append(field_obj)
        return self
    
    def create_namedtuple(self) -> Type[namedtuple]:
        """
        Create a namedtuple type from this specification.
        
        Returns:
            A namedtuple class with fields matching this specification
        """
        field_names = [f.name for f in self.fields]
        return namedtuple(self.name, field_names)
    
    def create_dataclass(self) -> Type:
        """
        Create a dataclass type from this specification.
        
        Returns:
            A dataclass with fields matching this specification
        """
        annotations = {}
        defaults = {}
        
        for field_obj in self.fields:
            annotations[field_obj.name] = field_obj.dtype
            if field_obj.default is not None:
                defaults[field_obj.name] = field_obj.default
        
        # Create the dataclass dynamically
        def __init__(self, **kwargs):
            for field_obj in self.fields:
                value = kwargs.get(field_obj.name)
                if value is None and field_obj.default is not None:
                    value = field_obj.default
                setattr(self, field_obj.name, value)
        
        def __repr__(self):
            field_strs = []
            for field_obj in self.fields:
                value = getattr(self, field_obj.name)
                field_strs.append(f"{field_obj.name}={value}")
            return f"{self.name}({', '.join(field_strs)})"
        
        # Create the class
        cls_dict = {
            '__init__': __init__,
            '__repr__': __repr__,
            '__annotations__': annotations,
            '_dynamics_spec': self,
        }
        
        # Add defaults as class attributes
        cls_dict.update(defaults)
        
        return type(self.name, (object,), cls_dict)
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate data against this specification.
        
        Args:
            data: Dictionary of field_name -> value
            
        Returns:
            Dictionary of field_name -> error_message for any validation errors
        """
        errors = {}
        
        for field_obj in self.fields:
            value = data.get(field_obj.name)
            
            # Check required fields
            if value is None and field_obj.default is None:
                errors[field_obj.name] = f"Required field '{field_obj.name}' is missing"
                continue
            
            # Skip validation if value is None and there's a default
            if value is None and field_obj.default is not None:
                continue
            
            # Validate the value
            if not field_obj.validate_value(value):
                type_name = field_obj.dtype.__name__
                bounds_str = f" (bounds: {field_obj.bounds})" if field_obj.bounds else ""
                errors[field_obj.name] = f"Invalid value for '{field_obj.name}': expected {type_name}{bounds_str}, got {type(value).__name__}"
        
        return errors
    
    def get_field_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed information about all fields.
        
        Returns:
            Dictionary mapping field names to their specifications
        """
        return {
            field_obj.name: {
                'type': field_obj.dtype.__name__,
                'unit': field_obj.unit,
                'description': field_obj.description,
                'default': field_obj.default,
                'bounds': field_obj.bounds
            }
            for field_obj in self.fields
        }
    
    def __repr__(self) -> str:
        return f"DynamicsSpec(name='{self.name}', fields={len(self.fields)})"

# Example usage and factory functions
class DynamicsSpecBuilder:
    """Builder class for creating common dynamics specifications."""
    
    @staticmethod
    def create_vehicle_state() -> DynamicsSpec:
        """Create a typical vehicle state specification."""
        return (DynamicsSpec("VehicleState", description="Vehicle state variables")
                .add_field("position_x", float, "m", description="X position")
                .add_field("position_y", float, "m", description="Y position")
                .add_field("velocity", float, "m/s", description="Forward velocity", bounds=(0, None))
                .add_field("yaw_rate", float, "rad/s", description="Yaw rate", bounds=(-10, 10))
                .add_field("steering_angle", float, "rad", description="Steering angle", bounds=(-1.57, 1.57)))
    
    @staticmethod
    def create_control_inputs() -> DynamicsSpec:
        """Create a typical control input specification."""
        return (DynamicsSpec("ControlInputs", description="Control input variables")
                .add_field("throttle", float, "percent", description="Throttle percentage", bounds=(0, 100))
                .add_field("brake", float, "percent", description="Brake percentage", bounds=(0, 100))
                .add_field("steering_command", float, "rad", description="Steering command", bounds=(-1.57, 1.57)))
    
    @staticmethod
    def create_derivatives() -> DynamicsSpec:
        """Create a typical derivatives specification."""
        return (DynamicsSpec("StateDerivatives", description="State derivative variables")
                .add_field("velocity_dot", float, "m/s^2", description="Velocity derivative")
                .add_field("yaw_rate_dot", float, "rad/s^2", description="Yaw rate derivative")
                .add_field("x_dot", float, "m/s", description="X position derivative")
                .add_field("y_dot", float, "m/s", description="Y position derivative"))
    
    @staticmethod
    def create_automaton_control_outputs() -> DynamicsSpec:
        """Create a automaton control spec"""
        return (DynamicsSpec("AutomatonControlOutputs", description="outputs for automaton spec")
                .add_field("velocity", float, unit="m/s", description="Velocity in meters per second")
                .add_field("yaw_rate", float, unit="rad/s", description="Yaw rate in radians per second"))

class DynamicsABC(ABC):
    """
    Abstract base class for hybrid automaton dynamics functions.
    
    Dynamics functions define how the system evolves over time in a given mode,
    based on current system state and possibly control inputs.
    
    Subclasses must implement the __call__ method to compute the output.
    """

    _init_input_spec: ClassVar[List[InputSpec]] = []
    _state_input_spec: ClassVar[List[InputSpec]] = []
    _state_buffer_spec: dict[str, deque]
    _dynamic_output_spec: ClassVar[Optional[DynamicsSpec]] = None

    def __init__(self, output_spec: Optional[DynamicsSpec] = None, **init_kwargs):
        """
        Initialize the dynamics function with the required output structure.
        
        Args:
            output_spec: DynamicsSpec defining the expected output structure.
            **init_kwargs: Additional configuration parameters.
        """
        self.logger = get_logger(self.__class__.__name__)
        self.is_initialized = False
        
        # Use class-level spec if no instance-level spec provided
        if output_spec is None:
            output_spec = self._dynamic_output_spec
        
        if output_spec is None:
            raise ValueError(f"{self.__class__.__name__} requires an output specification")
        
        self.output_spec = output_spec
        self.output_type = output_spec.create_namedtuple()
        
        self._validate_initialization(**init_kwargs)
        self._set_instance_initialization(**init_kwargs)
        self._set_instance_state_buffers()
        self.is_initialized = True
        self._dt = 0.1

    def _avg_dt_calc(self, current_dt: float, alpha: float = 0.1):
        """this functions averages the dt

        Args:
            current_dt (float): _description_
            alpha (float, optional): _description_. Defaults to 0.1.
        """
        self._avg_dt = alpha * current_dt + (1 - alpha) * self._avg_dt 

    def _set_instance_state_buffers(self):
        """creates buffers for states which can be utilized by the dynamic __call__ function.
        """
        self._state_buffer: Dict[str, deque] = {}

        for state_input in self._state_input_spec:
            self._state_buffer[state_input.name] = deque(maxlen=state_input.buffer_size)

    def _set_instance_initialization(self, **init_kwargs) -> None:
        """Set instance attributes from initialization kwargs."""
        for key, value in init_kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def __call__(self, **state_kwargs) -> Any:
        """
        Compute the dynamics output based on the current system state.
        
        Args:
            **state_kwargs: Keyword arguments representing state inputs.
        
        Returns:
            An instance of the configured output_type.
        
        Raises:
            RuntimeError: If not initialized
            ValueError / TypeError: If state inputs are invalid
        """
        if not self.is_initialized:
            raise RuntimeError(f"{self.__class__.__name__} must be initialized before calling")

        self._validate_states(**state_kwargs)
        # Implementation logic should return self.output_type(...)
    
    def _validate_initialization(self, **init_kwargs) -> None:
        """Validate static initialization parameters."""
        # Validate against _init_input_spec if defined
        if self._init_input_spec:
            for spec in self._init_input_spec:
                # Raise KeyError if required parameter is missing
                if spec.name not in init_kwargs:
                    raise KeyError(f"Missing required initialization parameter: '{spec.name}'")

                value = init_kwargs[spec.name]
                if not isinstance(value, spec.type):
                    raise TypeError(f"Parameter '{spec.name}' must be of type {spec.type.__name__}")
    
    def _validate_output(self, output):
        """Validate the output against the output specification."""
        if not isinstance(output, self.output_type):
            raise TypeError(f"Output must be of type {self.output_type.__name__}")
        
        # Create a dict from the namedtuple for validation
        output_dict = output._asdict()
        errors = self.output_spec.validate_data(output_dict)
        
        if errors:
            error_msgs = [f"{field}: {msg}" for field, msg in errors.items()]
            raise ValueError(f"Output validation failed: {'; '.join(error_msgs)}")

    def _validate_states(self, **state_kwargs) -> None:
        """Validate state inputs against the state input specification."""
        if not self.is_initialized:
            raise RuntimeError(f"{self.__class__.__name__} is not initialized")

        if self._state_input_spec:
            for spec in self._state_input_spec:
                # Raise KeyError if required parameter is missing
                if spec.name not in state_kwargs:
                    raise KeyError(f"Missing required state parameter: '{spec.name}'")

                value = state_kwargs[spec.name]
                if not isinstance(value, spec.type):
                    raise TypeError(f"State parameter '{spec.name}' must be of type {spec.type.__name__}")

    def create_output(self, **kwargs) -> Any:
        """
        Create an output instance with validation.
        
        Args:
            **kwargs: Field values for the output
            
        Returns:
            Validated output instance
        """
        # Fill in defaults
        output_data = {}
        for field in self.output_spec.fields:
            value = kwargs.get(field.name)
            output_data[field.name] = field.get_value_or_default(value)
        
        # Validate the data
        errors = self.output_spec.validate_data(output_data)
        if errors:
            error_msgs = [f"{field}: {msg}" for field, msg in errors.items()]
            raise ValueError(f"Output creation failed: {'; '.join(error_msgs)}")
        
        # Create the output
        output = self.output_type(**output_data)
        self._validate_output(output)
        return output

    @classmethod
    def init_input_spec_names(cls) -> List[InputSpec]:
        """Return a list of initialization inputs expected for the __init__, names and types"""
        return [init_input.name for init_input in cls._init_input_spec]

    @classmethod
    def init_input_spec_types(cls) -> List[str]:
        """returns a list of initialization input names passed for the __init__"""
        return [init_input.type for init_input in cls._init_input_spec]

    @classmethod
    def state_input_spec_names(cls) -> List[InputSpec]:
        """Return a list of state inputs expected for the __call__, names and types"""
        return [state_input.name for state_input in cls._state_input_spec]

    @classmethod
    def state_input_spec_types(cls) -> List[str]:
        """Returns a list of state input types required for the __call__, just names"""
        return [state_input.type for state_input in cls._state_input_spec]

    @classmethod
    def dynamic_output_spec_name(cls) -> str:
        return cls._dynamic_output_spec.name

    @classmethod
    def dynamic_output_spec_description(cls) -> str:
        return cls._dynamic_output_spec.description

    @classmethod
    def dynamic_output_spec_names(cls) -> List[str]:
        """
        Return the list of output field names from the current dynamic output specification.

        Returns:
            List of field names defined in the current _dynamic_output_spec.
        """
        if cls._dynamic_output_spec is None:
            return []
        return [field.name for field in cls._dynamic_output_spec.fields]

    @classmethod
    def dynamic_output_spec_types(cls) -> List[str]:
        if cls._dynamic_output_spec is None:
            return []
        return [field.dtype for field in cls._dynamic_output_spec.fields]
    
    @classmethod
    def dynamic_output_spec_units(cls) -> List[str]:
        if cls._dynamic_output_spec is None:
            return []
        return [field.unit for field in cls._dynamic_output_spec.fields]

    def get_dynamics_info(self) -> Dict[str, Any]:
        """Get information about this dynamics function."""
        class_doc = self.__class__.__doc__
        return {
            'class_name': self.__class__.__name__,
            'module': self.__class__.__module__,
            'is_initialized': self.is_initialized,
            'init_input_spec_names': self.init_input_spec_names(),
            'init_input_spec_types': self.init_input_spec_types(),
            'state_input_spec_names': self.init_input_spec_names(),
            'state_input_spec_types': self.init_input_spec_types(),
            'output_spec_name': self.dynamic_output_spec_name(),
            'output_spec_description': self.dynamic_output_spec_description(), 
            'output_spec_param_names': self.dynamic_output_spec_names(),
            'output_spec_param_types': self.dynamic_output_spec_types(),
            'output_spec_param_units': self.dynamic_output_spec_units(),
            'description': class_doc.strip().split('\n')[0] if class_doc else "No description",
        }

    def __repr__(self) -> str:
        output_name = self.output_type.__name__ if hasattr(self, 'output_type') else "Unknown"
        return f"{self.__class__.__name__}(output_type={output_name}, initialized={self.is_initialized})"

    def __str__(self) -> str:
        output_name = self.output_type.__name__ if hasattr(self, 'output_type') else "Unknown"
        return f"Dynamics Function: {self.__class__.__name__} (Output: {output_name})"


# Example implementation
class SimpleDynamics(DynamicsABC):
    """Example dynamics function for demonstration."""
    
    _dynamic_output_spec = DynamicsSpecBuilder.create_derivatives()
    
    def __call__(self, velocity: float, yaw_rate: float, position_x: float, position_y: float) -> Any:
        """Simple dynamics implementation."""
        super().__call__(velocity=velocity, yaw_rate=yaw_rate, position_x=position_x, position_y=position_y)
        
        # Simple dynamics: derivatives are just the current values
        return self.create_output(
            velocity_dot=0.0,  # No acceleration
            yaw_rate_dot=0.0,  # No angular acceleration
            x_dot=velocity,    # Forward velocity
            y_dot=0.0         # No lateral movement
        )


# Example usage demonstration
if __name__ == "__main__":
    # Create a dynamics function
    dynamics = SimpleDynamics()
    
    # Use it
    result = dynamics(velocity=10.0, yaw_rate=0.1, position_x=0.0, position_y=0.0)
    print(f"Result: {result}")
    
    # Get info
    info = dynamics.get_dynamics_info()
    print(f"Dynamics Info: {info}")
    
    # Create custom specifications
    custom_spec = (DynamicsSpec("CustomOutput")
                   .add_field("force", float, "N", description="Applied force")
                   .add_field("torque", float, "Nm", description="Applied torque"))
    
    # Create a custom dynamics class
    class CustomDynamics(DynamicsABC):
        def __call__(self, mass: float, moment: float) -> Any:
            super().__call__(mass=mass, moment=moment)
            return self.create_output(force=mass * 9.81, torque=moment * 0.1)
    
    custom_dynamics = CustomDynamics(output_spec=custom_spec)
    custom_result = custom_dynamics(mass=10.0, moment=5.0)
    print(f"Custom Result: {custom_result}")