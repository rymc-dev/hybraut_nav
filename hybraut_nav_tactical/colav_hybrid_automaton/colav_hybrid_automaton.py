import math
from geometry_msgs.msg import TwistStamped, PoseStamped
from typing import Dict
import numpy as np
from scipy.spatial.transform import Rotation as R
from typing import Optional


# guards
def heading_not_within_tolerance_guard(x: PoseStamped, aux_x: Dict, u: Dict, ctx: Dict, dt: float = 0.1):
        x: PoseStamped = x
        w: PoseStamped = aux_x.get('waypoint')

        # Extract positions
        xx = x.pose.position.x
        xy = x.pose.position.y

        wx = w.pose.position.x
        wy = w.pose.position.y

        # If waypoint at agent, aligned
        if xx == wx and xy == wy:
            return False

        # Compute headings
        r = R.from_quat(
            [x.pose.orientation.x,
            x.pose.orientation.y,
            x.pose.orientation.z,
            x.pose.orientation.w]
        )
        roll, pitch, yaw = r.as_euler('xyz', degrees=True)
        desired_heading = math.atan2(wy - xy, wx - xx)

        # For large tolerances, detect raw yaw > 180° via quaternion.w sign
        if ctx.get('heading_tolerance') >= math.pi:
            # if quaternion half-angle cos < 0, original yaw > π
            if agent_state.pose.orientation.w < 0:
                raw_yaw = wrapped_yaw + 2 * math.pi
            else:
                raw_yaw = wrapped_yaw
            error = raw_yaw - desired_heading
        else:
            # use wrapped error in [-π, π]
            error = delta_heading(
                x_a=ax, y_a=ay,
                theta_a=wrapped_yaw,
                x_w=wx, y_w=wy
            )

        # consider floating-point boundary: treat near-equal as within tolerance
        outside = abs(error) > self.__getattribute__('heading_tolerance')
        if outside and not math.isclose(abs(error), self.__getattribute__('heading_tolerance')):
            return True
        return False