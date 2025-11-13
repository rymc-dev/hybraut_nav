""" 


"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from statemachine import State
from typing import Optional, Callable, List, Any, Tuple
import asyncio


from typing import Optional, Callable, Any, Tuple, Dict

class HybridTransition:
    """ 
    Defines the transition logic for a hybrid automaton model.

    Args: 
        name: str
            human readable transition name for huamn viewing
        value: int 
            a simple storage/retrieval represenation of this transition, should be unique 
            for a hybrid automaton model
        to: HybridState
            a referece to a HybridState that this transition should transition to
        guard: Optional[Callable]
            an optional guard function that determines if guard is active or inactive
        reset: Optional[Callable]
            an optional reset function that determinal if reset is avaiable for during transition 


    Functions:

    """

    def __init__(
        self,
        name: str,
        value: int,
        to: str,
        guards: Optional[List[Callable[[Any], bool]]] = None,
        resets: Optional[List[Callable[[Any], Any]]] = None,
        priority: int = 1
    ):
        self.name = name
        self.value = value
        self.to = to
        self.guards = guards
        self.resets = resets
        self.priority = priority

    def is_enabled(self, x: Any, ctx: Optional[Any] = None) -> bool:
        """
        apply guard to continous state and/or auxielary context 
        to see if transition is enabled or not

        Args: 
            x: Any
                continous state information representation
            ctx: Optional[Any]
                auxilary information for the hybrid automaton model

        Outputs: 
            boolean: represents if transition is enabled
        """
        if self.guards is None:
            return True # pass through guard, always true if guard not given
        
        return all(guard(x, ctx) for guard in self.guards)
    
    def apply_reset(self, x: Any, u: Optional[Any], ctx: Optional[Any] = None, dt: Optional[float] = 0.1) ->  Tuple[Any, Any]: 
        """
        apply reset to continous states and/or auxielary context information 
        for the hybrid automaton model

        Args: 
            x: Any
                continous state information repesentation
            ctx: Optional[Any]
                auxielary context information represenation the for hybrid automaton

        Outputs:
            Tuple[x, ctx]: represents new continous states and auxielary states
        """
        if self.resets is None: 
            return x, ctx # pass through, reset just returns the x and ctx
        return self.resets(x, u, ctx, dt)
    
    def execute(self, x: Any, u: Optional[Any] = None, ctx: Optional[Any] = None, dt: Optional[float] = 0.1) -> Tuple[Any, Any, Any]:
        """ 
        execute applies resets to the current contious and auxielary states
        utilzing information regarding the automaton and also return the next state

        Args: 
            x: Any
                continous states representation
            u: Optional[Any]
                external inputs
            ctx: Optional[Any]
                auxiarly context of automaton
            dt: Optional[float] = 0.1
                the delta time in seconds
        """
        new_x, new_ctx = self.apply_reset(x, u, ctx, dt)
        return self.to, new_x, new_ctx
    
    def __repr__(self): 
        ... 

    def __str__(self): 
        ...

class HybridState:
    """ 
    HybridState is a discrete state represeting a control mode the hybrid
    automaton can be in. 

    Args: 
        name: str
            A human-readable representation of the state. Default is derived
            from the value
        value: int
            A specific value for representation of the state for retrieval/storage of it
        initial: Optional[bool]
            Set ``True`` if the state is the inital one, There must only be one
            state ever at a time, defaults to ``False``
        final: Optional[bool] 
            Set ``True`` to represent a final state. FIle states have no :ref: to transition
            starting from it, Defaults to ``False``
        flow: Optional[Callbable] 
            flow function utilized for calculation of continous state of the hybrid automaton, 
            defaults to ``none`` meaning continous dynamics return nothing
        invariants: Optional[List[Callable]] 
            invariant function utilzied while inside hybrid automaton state, can evaluate continous
            state and auxielary context of the environment and generate true/false values based on whether
            we should be in this state.
        transitions: Optional[HybridTransition]
            A list of HybridTransitions associated with this hybrid automaton state
        integration_method: Optional[Callable] 
            This is an optional function for continous dynamic simulation it is required if 
            automaton is simulation otherwise not if real time because continous state will be generated 
            by sensors and external data
        on_enter: Optional[Callable]
            One or more action callbacks assigned to be exectued when the state is activated
        on_exit: Optional[Callable] 
            One or more action callbacks assigned to be executed when the state is being exectued


    Functions: 
        evaluate_transitions(x: Any, ctx: Any) -> ...: 
            a coro async function for evaluation of transitions within for this state.#

        continous_dynamics(x: Any, Optional[Any], dt)
    """

    def __init__(
        self,
        name: str = "",
        value: int = 0,
        initial: bool = False,
        final: bool = False,
        flow: Optional[Callable] = None,
        invariants: Optional[List[Callable]] = None,
        transitions: Optional[List['HybridTransition']] = None,
        integartion_method: Optional[Callable] = None,
        on_enter: Optional[Callable] = None,
        on_exit: Optional[Callable] = None
    ):
        self.name = name
        self.value = value
        self.flow = flow
        self.invariants = invariants
        self.transitions = [] if transitions == None else transitions
        self.integration_method = integartion_method
        self.initial = initial
        self.final = final
        self.on_enter = on_enter
        self.on_exit = on_exit






    def add_transition(self, transition: HybridTransition): 
        self.transitions.append(transition)

    async def evaluate_transitions(self, x: Any, u: Optional[Any] = None, ctx: Optional[Any] = None, dt: float = 0.1) -> List[Tuple[HybridTransition, bool, Optional[Exception]]]:
        """
        Concurrently evaluate guards for each HybridTransition.

        Returns a list of tuples (transition, enabled, exception). If an exception
        occurred while evaluating a guard, `enabled` will be False and `exception`
        contains the caught exception.

        Args: 
            x: continous state
            ctx: auxielary context for this Hybrid Automaton to run
        """
        if not self.transitions:
            return []

        async def _eval(t: HybridTransition):
            try:
                enabled = bool(t.is_enabled(x, ctx))
                return (t, enabled, None)
            except Exception as e:
                return (t, False, e)

        coros = [_eval(t) for t in self.transitions]
        results = await asyncio.gather(*coros, return_exceptions=False)
        return results

    async def continuous_dynamics(self, x: Any, u: Optional[Any] = None,  ctx: Optional[Any] = None, dt: Optional[float] = None) -> Any:
        """
        Process continuous dynamics using current state and context.
        Synchronous function.

        Args: 
            x: Any  
                continous dynamics representation for this model
            u: Optional[Any]
                optional command inputs like rudder, thrust, etc....
            dt: Optional[float]
                optional delta time for continous dynamics that required future predictions,
                dt represented in seconds
            ctx: Optional[Any]
                auxielary contexts like goal waypoints, or some other params for the continous dynamics.
        """
        if self.flow is None:
            return x if x is not None else []
        return self.flow(x, u, dt, ctx)

    async def check_invariants(self, x: Any, u: Optional[Any] = None, ctx: Optional[Any] = None, dt: float = 0.1) -> bool:
        """
        a coro async function for checking invariants for this HybridState

        Args: 
            x: Optional[Any]
                continous state represntation
            ctx: Optional[Any]
                auxielary context information

        returns: 
        bool: True if invariant holds, else False
        """
    
        if not self.invariants:
            return []

        async def _eval(i: Callable):
            try:
                enabled = bool(i(x, ctx))
                return (i, enabled, None)
            except Exception as e:
                return (i, False, e)

        coros = [_eval(i) for i in self.invariants]
        results = await asyncio.gather(*coros, return_exceptions=False)
        return results
    
class HybridAutomaton: 
    """ 
    model of the hybrid automaton 

    args: 
        name: str
            human readable representaiton of the hybrid automaton model
        value: int
            value respetnation of the hybrid automaton, clearly shows the model 
            for storage purposes in case you have sevelar models running at the same time
        states: List[HybridState]
            these are the Hybrid STates of the automaton, these represent the discrete modes
            of the automaton 

        on_entry: Optional[Callable]
            on entry callback function for when evaluation_loop_worker starts

        on_exit: Optional[Callable]
            on exit callback function for when evaluation_loop_worker completes

    
    
    functions:
        evaluation_loop_worker(self): 
            async coro worker for running the automaton 
            using asyncio

    
    """

    _q = None
    _x_t0 = None
    _x = None
    _u_t0 = None
    _u = None
    _ctx_t0 = None
    _ctx = None
    _dt = None
    _xdot = None
    _active = False
    _elapsed_time_active = None
    _elapsed_time_since_transition = None
    
    def __init__(self, name: str, value: int, states: List[HybridTransition], on_entry: Optional[Callable] = None, on_exit: Optional[Callable] = None):
        """ """
        
        self.NAME = name
        self.VALUE = value
        self.Q = states

        init_idx = [i for i, s in enumerate(self.Q) if getattr(s, "initial", False)]
        cnt_init = len(init_idx)
        if cnt_init == 0: 
            raise ValueError("invalid HybridAutomaton initialization, need 1 initial state, got 0.")
        if cnt_init > 1: 
            raise ValueError(f"invalid HybridAutomaton initialization, need 1 initial state, got {cnt_init}")
        
        self._Q_T0 = self.Q[init_idx[0]]
        self._ON_ENTRY = on_entry
        self._ON_EXIT = on_exit

    """ === getters and setters === """
    @property
    def x(self): 
        return self._x
    
    @property
    def u(self):
        return self._u

    @property
    def ctx(self):
        return self._ctx
    
    @property
    def dt(self):
        return self._dt

    @property
    def xdot(self): # NOTE: continous dynamics has not setter, becuase this is internally generated
        return self._xdot
    
    def set_continous_state(self, new_continous_state: Any): # NOTE: This setter should only be avialable if real_time hybrid automaton.
        """explcit setter for the _x attribute value which is the continous state values of the hybrid automaton"""
        self._x = new_continous_state
    
    def set_control_input(self, new_ctrl_input: Any): 
        """explicity setter for the internal _u control input vector"""
        self._u = new_ctrl_input
    
    def set_aux_context(self, new_aux_ctx: Dict[str, Any]):
        """explicit setter for the internal _ctx auxiliary context for the hybrid automaton""" 
        self._ctx = new_aux_ctx

    def set_dt(self, new_dt: float):
        """explicit setter for internal dt, used for timing of evalution loop and calculations"""
        self._dt = new_dt


    async def trigger_transition(self): ... 

    async def trigger_reset(self): 
        ... 

    async def step_evalution(self): 
        ... 

    async def evluation_loop_worker(
        self,
        x_t0: Any,
        u_t0: Optional[Any] = None,
        ctx_t0: Optional[Any] = None,
        dt: float = 0.1
    ):
        """ 
        Async evaluation loop worker for hybrid automaton.

        Args: 
            x_t0: initial continuous state value
            u_t0: initial input
            ctx_t0: auxiliary context for hybrid automaton
        """
        
        print(f"starting {self.NAME}")

        if self._ON_ENTRY is not None:
            self._ON_ENTRY()

        self.active = True

        self._q = self._Q_T0
        self._x   = x_t0
        self._u   = u_t0
        self._ctx = ctx_t0
        self._dt  = dt

        while self.active:

            # -------------------------------------------------------------
            # 1️⃣ Continuous dynamics (ALWAYS evaluated first)
            # -------------------------------------------------------------
            self._xdot = await self._q.continuous_dynamics(
                self._x, self._u, self._ctx, self._dt
            )

            # TODO: check here if there is integration/ real_time param is set to true or false
            # for now assuming closed loop control with simulation, If it's not real time
            # we need here to do an update on the continous state.

            # -------------------------------------------------------------
            # 2️⃣ Check transitions (guards)
            # -------------------------------------------------------------
            D_eval = await self._q.evaluate_transitions(
                self._x, self._u, self._ctx, self._dt
            )

            # Collect all transitions whose guard evaluates to True
            D_active = [t[0] for t in D_eval if t[1] == True]

            if D_active:
                # Guard transitions have priority over invariants
                if len(D_active) == 1:
                    d = D_active[0]
                else:
                    def resolve_transition_priority(D_active):
                        to = None
                        lowest_priority = None
                        for t in D_active:
                            if lowest_priority is None:
                                lowest_priority = t.priority
                                to = t
                                continue

                            if lowest_priority > t.priority: 
                                lowest_priority = t.priority
                                to = t

                        return to

                    # TODO: implement priority logic if multiple guards active
                    d = resolve_transition_priority(D_active)

                # ---------------------------------------------------------
                # 2b️⃣ Execute transition (apply reset, change state)
                # ---------------------------------------------------------
                new_q, new_x, new_ctx = d.execute(
                    self._x, self._u, self._ctx, self._dt
                )

                # Update automaton state
                self._q = new_q
                self._x = new_x
                self._ctx = new_ctx

                # Invoke state entry callback
                if new_q.on_enter is not None:
                    new_q.on_enter()

                # Continue to next iteration (skip invariant check)
                continue

            # -------------------------------------------------------------
            # 3️⃣ No transition fired → check invariant of current state
            # -------------------------------------------------------------
            invariants_ok = await self._q.check_invariants(
                self._x, self._u, self._ctx, self._dt
            )
            self.invariants = invariants_ok

            if not invariants_ok:
                # Invariant violated → forced exit or error
                if self._q.final:
                    # Proper termination
                    print(f"{self.NAME} reached final state {self._q.name}")
                    self.active = False
                    break
                else:
                    raise RuntimeError(
                        f"Invariant violated in mode '{self._q.name}' "
                        "with no valid outgoing transition."
                    )

            # -------------------------------------------------------------
            # 4️⃣ Real-time pacing / cooperative async yielding
            # -------------------------------------------------------------
            await asyncio.sleep(self.dt)

        # -------------------------------------------------------------
        # On exit
        # -------------------------------------------------------------
        if self._ON_EXIT is not None:
            self._ON_EXIT()


def main():
    def guard(*args, **kwargs):
        return True

    state_1 = HybridState(
        name="start",
        value=0,
        initial=True
    )


    state_2 = HybridState(
        name = "end",
        value=1,
        final=True
    )


    state_1.add_transition(
        HybridTransition(
            name="transition_1",
            value=1,
            to=state_2,
            guards=[guard],
        )
    )
    state_1.add_transition(
        HybridTransition(
                name="transition_1",
                value=2,
                to=state_2,
                guards=[guard],
                priority=2
            )
    )


    ha = HybridAutomaton(
        name="tb3 automaton",
        value=0,
        states=[state_1, state_2],
    )
    import numpy as np
    # position [x, y, z] and quaternion [qx, qy, qz, qw]
    x_t0 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
    x_u0 = None
    ctx_t0 = {
        'waypoint': np.array([0.0, 0.0]),
        'virtual_waypoint': np.array([0.0, 0.0])
    }
    dt = 0.1  # Adjusted to a small positive value for time step


    import threading

    thread_1 = threading.Thread(
        target=asyncio.run(
            ha.evluation_loop_worker(x_t0, x_u0, ctx_t0, dt)
        )
    ).start()

    thread_2 = threading.Thread(
        target=asyncio.run(
            ha.evluation_loop_worker(x_t0, x_u0, ctx_t0, dt)
        )
    ).start()

    import time
    time.sleep(10.0)

if __name__ == '__main__':
    main()
