import asyncio
import numpy as np
from typing import Optional, Any, Callable, Tuple
from statemachine import State, StateMachine
from typing import Dict, List





def flow_to_waypoint(x, u=None, dt=None, context=None):
    if context is None or "goal" not in context:
        raise ValueError("Goal waypoint required in context.")
    goal = context["goal"]
    dx = goal["x"] - x["x"]
    dy = goal["y"] - x["y"]
    distance = np.hypot(dx, dy)
    heading_error = np.arctan2(dy, dx) - x["yaw"]
    return {
        "distance_to_goal": distance,
        "heading_error": heading_error,
        "goal_reached": distance < 2.0
    }

state_1 = HybridState(
    "Initial State",
    flow=flow_to_waypoint,
    invariant=lambda x, ctx=None: True,
    transitions=[
        HybridTransition(
            name='initial_transition',
            to="Goal State",
            guard=lambda x, ctx=None: True,
        )
    ]
)
state_2 = HybridState(
    "Goal State"
)

async def worker():
    transition_evaluations = await state_1.evaluate_transitions(
        x=None,
        ctx=None
    )

    print (transition_evaluations)

asyncio.run(worker())



class HybridAutomaton(): 
    """ 
    real time hybrid automaton state machine
    model
    """

    def __init__(self):
        self.transitions_map: Dict[str, HybridTransition] = {} # can be either a simple transition name of transition wrapper
        self._event_detection = True
        self._event_tolerance = 1e-6
        
        self._transition_event = asyncio.Event()
        self._invariant_failed_event = asyncio.Event()

    async def evaluation_loop(self): 
        while True: 

    async def wait_for_transition(self):
        while True: 
            await self._transition_event 

            await self.trigger_transtion()

            self._transition_event.clear()

    async def trigger_transtion(self):


    async def trigger_reset(self): 
        self._

#     async def wait_for_transition():

#     @property
#     def continuous_state(self) -> Any:
#         """
#         Override this property to return your continuous state variables.
#         Can be a scalar, numpy array, or any custom type.
#         """
#         raise NotImplementedError("Must implement continuous_state property")
    
#     @continuous_state.setter
#     def continuous_state(self, value: Any):
#         """Override this setter to update continuous state"""
#         raise NotImplementedError("Must implement continuous_state setter")
    
#     def get_current_hybrid_state(self) -> HybridState: 
#         """Get the current HybridState object"""
#         return self.current_state._state()
    
#     async def check_guards(self) -> Optional[Tuple[str, HybridTransition]]: 
#         """
#         check all guards and return enabled transition with highest priority
        
#         Returns: 
#         --------
#         Optional[Tuple[str, HybridTransition]] : (event_name, transition) or None
#         """
#         enabled = []
#         x = self.continuous_state
#         ctx = self.auxielary_context
        
#         for event_name, transition in self.transitions_map.items():
#             # Check if this transition is from current state
#             try:
#                 # Get the transition object from state machine
#                 if hasattr(self, event_name) and transition.is_enabled(x):
#                     enabled.append((event_name, transition))
#             except Exception:
#                 continue
        
#         if not enabled:
#             return None
        
#         # Return highest priority transition
#         return max(enabled, key=lambda t: t[1].priority)


# class CustomHybridAutomaton(HybridAutomaton):
#     def __init__(self):
#         super().__init__()
#         self._continuous_state = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])


#     @property # getter
#     def continuous_state(self) -> Any:
#         """Return the current continuous state"""
#         return self._continuous_state

#     @continuous_state.setter # setter
#     def continuous_state(self, value: Any):
#         """Update the continuous state"""
#         self._continuous_state = value


# # ---- Example flow function ----
# def flow_to_waypoint(x, u=None, dt=None, context=None):
#     if context is None or "goal" not in context:
#         raise ValueError("Goal waypoint required in context.")
#     goal = context["goal"]
#     dx = goal["x"] - x["x"]
#     dy = goal["y"] - x["y"]
#     distance = np.hypot(dx, dy)
#     heading_error = np.arctan2(dy, dx) - x["yaw"]
#     return {
#         "distance_to_goal": distance,
#         "heading_error": heading_error,
#         "goal_reached": distance < 2.0
#     }

# # ---- Instantiate hybrid state ----
# state = HybridState(
#     "Initial State",
#     flow=flow_to_waypoint,
#     invariant=lambda x, ctx=None: True
# )

# # ---- Example async worker loop ----
# async def step_worker(sensor_state, context, dt=0.1):
#     while True:
#         output = state.continuous_dynamics(sensor_state, dt=dt, ctx=context)
#         invariant_ok = state.check_invariant(sensor_state, ctx=context)
#         print("Flow:", output, "Invariant:", invariant_ok)
#         await asyncio.sleep(dt)  # yield to event loop

# # ---- Run example ----
# sensor_state = {"x": 0.0, "y": 0.0, "yaw": 0.0}
# context = {"goal": {"x": 10.0, "y": 10.0}}

# asyncio.run(step_worker(sensor_state, context))
