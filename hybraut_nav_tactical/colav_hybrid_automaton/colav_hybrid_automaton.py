
from geometry_msgs.msg import TwistStamped, PoseStamped
from typing import Dict
from typing import Optional
from hybrid_automaton import Automaton, State, Transition
from types import SimpleNamespace as SN
import math
import numpy as np
from scipy.spatial.transform import Rotation as R

import math
import numpy as np
from typing import List


def heading_not_within_tolerance_guard(x: list[float, float, float], aux_x: Dict = None, ctx: Dict= None,  u: Dict=None, dt: float=0.1):
    """ 
    guard function for hybrid automaton which checks if a heading provided is 
    not within a heading tolerance

    Output: 
        Returns True if heading error is OUTSIDE tolerance.

    Args: 
        x: List
            represents continous state of agent in this case
            agent continous state is [x: float, y: float, theta: float]
            theta should be in radians
        aux_x: Dict
            represents auxielary continous states within state space 
            in this case we utilize aux_x["waypoints"] = [[wx, wy], [wx, wy]]
            to get the current_waypoint we are navigating towards
        ctx: Dict
            represents context values of the hybrid automaton, this can include
            automaton configuration and also details regarding time since last transition
            and so on. In this case we use ctx['cfg']['heading_tolerance'] which is a float
            value representing heading_tolerance in radians. 
        u: Dict
            this are control inputs we expected, this this case is is None by default and not used
        dt: float
            delta time between guard checks, this is not used within this guard however, just 
            a required arg for integration with automaton guards

    Raises: 
        ...
    """

    if aux_x is None or "waypoints" not in aux_x:
        return False

    xx, xy, yaw = x            # current position + heading
    wx, wy = aux_x["waypoints"][-1] # waypoint position

    # If exactly at the waypoint → no heading mismatch
    if xx == wx and xy == wy:
        return False

    # desired heading (radians)
    desired = math.atan2(wy - xy, wx - xx)

    # normalized heading error in [-π, π]
    error = math.atan2(math.sin(desired - yaw), math.cos(desired - yaw))

    # True only if heading error exceeds tolerance
    return abs(error) > ctx["heading_tolerance"]

def heading_within_tolerance_guard(x: List[float, float, float], aux_x: Dict, ctx: Dict = None,  u: Dict = None, dt: float=0.1):
    """ 
    Guard function for hybrid automaton which checks if a heading provided is 
    within a heading tolerance.

    Output: 
        Returns True if heading error is WITHIN tolerance.

    Args: 
        x: List
            Represents continuous state of the agent.
            Agent continuous state is [x: float, y: float, theta: float]
            theta should be in radians.
        aux_x: Dict
            Represents auxiliary continuous states.
            Uses aux_x["waypoints"] = [[wx, wy], [wx, wy]] for current navigation targets.
        ctx: Dict
            Context values of the hybrid automaton.
            Uses ctx['cfg']['heading_tolerance'] (float, in radians).
        u: Dict
            Control inputs (unused for this guard).
        dt: float
            Delta time between guard checks (unused).

    Raises:
        ...
    """

    if aux_x is None or "waypoints" not in aux_x:
        return False

    xx, xy, yaw = x              # current position + heading
    wx, wy = aux_x["waypoints"][-1]   # waypoint position

    # If exactly at the waypoint → trivially within tolerance
    if xx == wx and xy == wy:
        return True

    # desired heading (radians)
    desired = math.atan2(wy - xy, wx - xx)

    # normalized heading error in [-π, π]
    error = math.atan2(math.sin(desired - yaw), math.cos(desired - yaw))

    # True when heading error is WITHIN tolerance
    return abs(error) <= ctx["cfg"]["heading_tolerance"]

def virtual_waypoints_guard(aux_x: Dict, x: List[float, float, float] = None, ctx: Dict = None, u: Dict = None, dt: float = None):
    """
    validate is there are virtual waypoints in the waypoints list 
    """
    return len(aux_x['waypoints']) > 1

def waypoint_reached_guard(x: List[float, float, float], aux_x: Dict, ctx: Dict, u: Dict = None, dt: float = 0.1):
    """
    automaton for 
    """
    waypoints_reached_acceptance_radius = ctx["cfg"]["acceptance_radius"] 

    return waypoints_reached_acceptance_radius >= math.dist(
        x[0:1], aux_x['waypoints'][-1]
    )


# from types import SimpleNamespace as SN
# import math

# # ============ helper Pose / Waypoint generator ============
# def make_pose(x, y, yaw_rad):
#     quat = R.from_euler('xyz', [0, 0, yaw_rad]).as_quat()
#     return SN(pose=SN(
#         position=SN(x=x, y=y, z=0),
#         orientation=SN(x=quat[0], y=quat[1], z=quat[2], w=quat[3])
#     ))

# # ============ test cases ============
# ctx = {"heading_tolerance": math.radians(10)}  # 10° tolerance

# agent = make_pose(0, 0, yaw_rad=0)  # facing +X direction

# tests = [
#     ("Aligned (0° error)", make_pose(10, 0, 0)),
#     ("Small error (5°)", make_pose(10, math.tan(math.radians(5))*10, 0)),
#     ("Large error (45°)", make_pose(10, 10, 0)), 
#     ("Opposite direction (180°)", make_pose(-10, 0, 0)),
# ]

# for name, waypoint in tests:
#     ok = heading_not_within_tolerance_guard(agent, ctx, aux_x={"waypoint": waypoint})
#     print(f"{name:25s} => {ok}")


# ============ helpers ============
def make_pose(x, y, yaw_rad):
    quat = R.from_euler('xyz', [0, 0, yaw_rad]).as_quat()
    return SN(pose=SN(
        position=SN(x=x, y=y, z=0),
        orientation=SN(x=quat[0], y=quat[1], z=quat[2], w=quat[3])
    ))


# ============ Set up Automaton ============
def on_A_enter():
    print("Entered State A")

def on_B_enter():
    print("➡️  TRANSITIONED to State B")


A = State("A", initial=True, on_enter=on_A_enter)
B = State("B", on_enter=on_B_enter)

# Transition guarded by your function
A.add_transition(
    Transition(
        name="A_to_B",
        to_state=B,
        guards=[heading_not_within_tolerance_guard]
    )
)

ha = Automaton(
    name="HeadingTestHA",
    states=[A, B],
    real_time_mode=False,
    dt=0.1
)

# ============ Context + Inputs ============
ctx = {"heading_tolerance": math.radians(10)}   # 10 degree tolerance

agent = make_pose(0, 0, yaw_rad=0)               # facing +X direction

# CHOOSE waypoint:
# -------------------------
# Case 1: within tolerance → no transition
# waypoint = make_pose(10, math.tan(math.radians(5))*10, 0)

# Case 2: outside tolerance → SHOULD transition
waypoint = make_pose(10, 10, 0)

aux_x = {"waypoint": waypoint}


# ============ RUN ============
ha.activate(x0=agent, aux_x0=aux_x)

print("\nStarting automaton test...\n")

for i in range(5):
    result = ha.step()
    print(f"Step {i}: state={ha.q.name}")

    if result and result.transition_taken:
        print(f"⚡ Transition fired: {result.transition_taken.name}")
        break

print("\nTest complete.")
