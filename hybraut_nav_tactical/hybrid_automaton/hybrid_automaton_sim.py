"""
Hybrid Automaton Extension for python-statemachine

A library for creating hybrid systems with continuous dynamics and discrete transitions.
Compatible with python-statemachine library.

This version of the automaton is a self contained simulation. It generates next continous states 
using integration since there is no continous state updates manually this is for self contained simulation.
"""

import numpy as np
from typing import Callable, Optional, Dict, Any, Tuple
from statemachine import StateMachine, State
from enum import Enum

# --- Integration Methods -------------------------------------------------
class IntegrationMethod(Enum):
    """Available numerical integration methods"""
    EULER = "euler"
    RK4 = "rk4"
    MIDPOINT = "midpoint"


class Integrator:
    """Numerical integration methods for continuous dynamics"""
    
    @staticmethod
    def euler(flow: Callable, x: Any, dt: float) -> Any:
        """Forward Euler method"""
        dx = flow(x)
        if isinstance(x, np.ndarray):
            return x + dx * dt
        return x + dx * dt
    
    @staticmethod
    def rk4(flow: Callable, x: Any, dt: float) -> Any:
        """4th order Runge-Kutta method"""
        k1 = flow(x)
        k2 = flow(x + 0.5 * dt * k1)
        k3 = flow(x + 0.5 * dt * k2)
        k4 = flow(x + dt * k3)
        
        if isinstance(x, np.ndarray):
            return x + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        return x + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
    
    @staticmethod
    def midpoint(flow: Callable, x: Any, dt: float) -> Any:
        """Midpoint method (2nd order)"""
        k1 = flow(x)
        k2 = flow(x + 0.5 * dt * k1)
        
        if isinstance(x, np.ndarray):
            return x + dt * k2
        return x + dt * k2
    
# --- Hybrid State -------------------------------------------------
class HybridState(State):
    """
    A state with continuous dynamics (flow) and invariant conditions.
    
    Parameters:
    -----------
    flow : Callable[[Any], Any], optional
        Continuous dynamics function dx/dt = flow(x)
    invariant : Callable[[Any], bool], optional
        Invariant condition that must hold while in this state
    integration_method : IntegrationMethod, optional
        Numerical integration method (default: EULER)
    """
    
    def __init__(
        self, 
        *args, 
        flow: Optional[Callable[[Any], Any]] = None,
        invariant: Optional[Callable[[Any], bool]] = None,
        integration_method: IntegrationMethod = IntegrationMethod.EULER,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.flow = flow
        self.invariant = invariant
        self.integration_method = integration_method
    
    def integrate(self, x: Any, dt: float) -> Any:
        """
        Integrate continuous dynamics one time step
        
        Parameters:
        -----------
        x : Any
            Current continuous state
        dt : float
            Time step
            
        Returns:
        --------
        Any : Updated continuous state
        """
        if self.flow is None:
            return x
        
        # Select integration method
        if self.integration_method == IntegrationMethod.EULER:
            return Integrator.euler(self.flow, x, dt)
        elif self.integration_method == IntegrationMethod.RK4:
            return Integrator.rk4(self.flow, x, dt)
        elif self.integration_method == IntegrationMethod.MIDPOINT:
            return Integrator.midpoint(self.flow, x, dt)
        else:
            return Integrator.euler(self.flow, x, dt)
    
    def check_invariant(self, x: Any) -> bool:
        """
        Check if invariant condition holds
        
        Parameters:
        -----------
        x : Any
            Current continuous state
            
        Returns:
        --------
        bool : True if invariant holds or no invariant defined
        """
        if self.invariant is None:
            return True
        return self.invariant(x)

# --- Hybrid Transition -------------------------------------------------
class HybridTransition:
    """
    Represents a transition with guard and optional reset map
    
    Parameters:
    -----------
    guard : Callable[[Any], bool]
        Guard condition for transition
    reset : Callable[[Any], Any], optional
        Reset map applied during transition
    priority : int, optional
        Priority for resolving conflicts (higher = more priority)
    """
    
    def __init__(
        self,
        guard: Callable[[Any], bool],
        reset: Optional[Callable[[Any], Any]] = None,
        priority: int = 0
    ):
        self.guard = guard
        self.reset = reset
        self.priority = priority
    
    def is_enabled(self, x: Any) -> bool:
        """Check if guard condition is satisfied"""
        return self.guard(x)
    
    def apply_reset(self, x: Any) -> Any:
        """Apply reset map to continuous state"""
        if self.reset is None:
            return x
        return self.reset(x)

# --- Hybrid Automaton Base Class -------------------------------------------------
class HybridAutomaton(StateMachine):
    """
    Base class for hybrid automata with continuous and discrete dynamics.
    
    Subclass this and define HybridState instances and transitions.
    Override continuous_state property to define your continuous variables.
    
    Example:
    --------
    class Thermostat(HybridAutomaton):
        heating = HybridState("Heating", initial=True, flow=lambda T: 0.1*(25-T))
        cooling = HybridState("Cooling", flow=lambda T: -0.07*(T-15))
        
        cool = heating.to(cooling)
        heat = cooling.to(heating)
        
        def __init__(self):
            self.T = 20.0
            super().__init__()
            self.transitions_map = {
                "cool": HybridTransition(guard=lambda T: T >= 22),
                "heat": HybridTransition(guard=lambda T: T <= 18)
            }
        
        @property
        def continuous_state(self):
            return self.T
        
        @continuous_state.setter
        def continuous_state(self, value):
            self.T = value
    """
    
    def __init__(self):
        super().__init__()
        self.transitions_map: Dict[str, HybridTransition] = {}
        self._integration_method = IntegrationMethod.EULER
        self._event_detection = True
        self._event_tolerance = 1e-6
    
    @property
    def continuous_state(self) -> Any:
        """
        Override this property to return your continuous state variables.
        Can be a scalar, numpy array, or any custom type.
        """
        raise NotImplementedError("Must implement continuous_state property")
    
    @continuous_state.setter
    def continuous_state(self, value: Any):
        """Override this setter to update continuous state"""
        raise NotImplementedError("Must implement continuous_state setter")
    
    def get_current_hybrid_state(self) -> HybridState:
        """Get the current HybridState object"""
        return self.current_state._state()
    
    def check_guards(self) -> Optional[Tuple[str, HybridTransition]]:
        """
        Check all guards and return enabled transition with highest priority
        
        Returns:
        --------
        Optional[Tuple[str, HybridTransition]] : (event_name, transition) or None
        """
        enabled = []
        x = self.continuous_state
        
        for event_name, transition in self.transitions_map.items():
            # Check if this transition is from current state
            try:
                # Get the transition object from state machine
                if hasattr(self, event_name) and transition.is_enabled(x):
                    enabled.append((event_name, transition))
            except Exception:
                continue
        
        if not enabled:
            return None
        
        # Return highest priority transition
        return max(enabled, key=lambda t: t[1].priority)
    
    def find_event_time(
        self,
        event_name: str,
        transition: HybridTransition,
        dt: float,
        tolerance: float = 1e-6,
        max_iter: int = 50
    ) -> float:
        """
        Use bisection to find exact time when guard becomes true
        
        Parameters:
        -----------
        event_name : str
            Name of the event/transition
        transition : HybridTransition
            The transition object
        dt : float
            Time step
        tolerance : float
            Convergence tolerance
        max_iter : int
            Maximum iterations
            
        Returns:
        --------
        float : Time when event occurs (between 0 and dt)
        """
        x0 = self.continuous_state
        state = self.get_current_hybrid_state()
        
        # Check if guard already satisfied
        if transition.is_enabled(x0):
            return 0.0
        
        # Binary search
        t_low, t_high = 0.0, dt
        
        for _ in range(max_iter):
            t_mid = (t_low + t_high) / 2
            x_mid = state.integrate(x0, t_mid)
            
            if transition.is_enabled(x_mid):
                t_high = t_mid
            else:
                t_low = t_mid
            
            if t_high - t_low < tolerance:
                break
        
        return (t_low + t_high) / 2
    
    def step(self, dt: float, check_invariant: bool = True) -> bool:
        """
        Execute one time step of hybrid dynamics
        
        Parameters:
        -----------
        dt : float
            Time step
        check_invariant : bool
            Whether to check invariant conditions
            
        Returns:
        --------
        bool : True if a transition occurred
        """
        state = self.get_current_hybrid_state()
        x = self.continuous_state
        
        # Check invariant
        if check_invariant and not state.check_invariant(x):
            # raise RuntimeError(
            #     f"Invariant violated in state {state.id} at x={x}"
            # )
            print (f"Invariant violated in state {state.id} at x={x}")
        
        # Check for enabled transitions
        transition_info = self.check_guards()
        
        if transition_info is not None:
            event_name, transition = transition_info
            
            # Find exact event time if event detection enabled
            if self._event_detection:
                t_event = self.find_event_time(
                    event_name, 
                    transition, 
                    dt, 
                    self._event_tolerance
                )
            else:
                t_event = 0.0
            
            # Integrate up to event time
            if t_event > 0:
                x_at_event = state.integrate(x, t_event)
                self.continuous_state = x_at_event
            
            # Apply reset map
            x_reset = transition.apply_reset(self.continuous_state)
            self.continuous_state = x_reset
            
            # Trigger transition
            transition_func = getattr(self, event_name)
            transition_func()
            
            # Integrate remainder of time step in new state
            remaining_dt = dt - t_event
            if remaining_dt > 0:
                new_state = self.get_current_hybrid_state()
                x_final = new_state.integrate(self.continuous_state, remaining_dt)
                self.continuous_state = x_final
            
            return True
        else:
            # No transition, just integrate
            x_next = state.integrate(x, dt)
            self.continuous_state = x_next
            return False
    
    def simulate(
        self, 
        duration: float, 
        dt: float,
        record_states: bool = True
    ) -> Dict[str, np.ndarray]:
        """
        Simulate the hybrid automaton for a given duration
        
        Parameters:
        -----------
        duration : float
            Total simulation time
        dt : float
            Time step
        record_states : bool
            Whether to record state history
            
        Returns:
        --------
        Dict[str, np.ndarray] : Dictionary with 'time', 'continuous', 'discrete'
        """
        n_steps = int(duration / dt)
        times = np.arange(n_steps) * dt
        
        if record_states:
            continuous_history = []
            discrete_history = []
            
            for _ in range(n_steps):
                continuous_history.append(self.continuous_state)
                discrete_history.append(self.current_state.id)
                self.step(dt)
            
            return {
                'time': times,
                'continuous': np.array(continuous_history),
                'discrete': discrete_history
            }
        else:
            for _ in range(n_steps):
                self.step(dt)
            return {'time': times}
    
    def set_integration_method(self, method: IntegrationMethod):
        """Set the integration method for all states"""
        self._integration_method = method
        for state in self.states:
            if isinstance(state, HybridState):
                state.integration_method = method
    
    def enable_event_detection(self, enabled: bool = True, tolerance: float = 1e-6):
        """Enable/disable event detection for precise guard transitions"""
        self._event_detection = enabled
        self._event_tolerance = tolerance


