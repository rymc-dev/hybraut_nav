# from colav_hybrid_automaton.automaton.resets import (
#     GenerateVirtualWaypointReset,
#     ResetABC
# )
# from typing import Dict
# import pytest
# from colav_interfaces.msg import WaypointsState as ROSWaypointsState
# from colav_interfaces.msg import (
#     AgentState as ROSAgentState,
#     ObstaclesState as ROSObstaclesState,
#     UnsafeSetState as ROSUnsafeSetState,
#     WaypointsState as ROSWaypointsState,
#     Waypoint as ROSWaypoint
# )
# from geometry_msgs.msg import Point, Pose, Quaternion
# from std_msgs.msg import Float64MultiArray
# import numpy as np
# import pytest

# def create_intercepting_polygon_points(agent_pos, waypoint_pos, polygon_center, polygon_size=20.0):
#     """
#     Create a square polygon that intercepts the line between agent and waypoint.
    
#     Args:
#         agent_pos: (x, y) tuple of agent position
#         waypoint_pos: (x, y) tuple of waypoint position  
#         polygon_center: (x, y) tuple where polygon should be centered
#         polygon_size: side length of the square polygon
    
#     Returns:
#         List of (x, y) points forming a square polygon
#     """
#     cx, cy = polygon_center
#     half_size = polygon_size / 2
    
#     # Create square vertices (counter-clockwise)
#     vertices = [
#         (cx - half_size, cy - half_size),  # bottom-left
#         (cx + half_size, cy - half_size),  # bottom-right  
#         (cx + half_size, cy + half_size),  # top-right
#         (cx - half_size, cy + half_size),  # top-left
#     ]
    
#     return vertices

# def create_agent_state_with_pose(x=0.0, y=0.0, heading=0.0):
#     """Create an agent state with specified position and heading."""
#     agent_state = ROSAgentState()
#     agent_state.pose = Pose()
#     agent_state.pose.position = Point(x=x, y=y, z=0.0)
    
#     # Convert heading to quaternion (assuming heading is in radians, yaw only)
#     qz = np.sin(heading / 2.0)
#     qw = np.cos(heading / 2.0)
#     agent_state.pose.orientation = Quaternion(x=0.0, y=0.0, z=qz, w=qw)
    
#     return agent_state

# @pytest.mark.parametrize(
#     "init_kwargs, state_kwargs, expected_reset_output, test_description",
#     [
#         # Test 1: Basic intercepting unsafe set
#         (
#             {
#                 'longitudinal_offset_distance': 10.0,
#                 'lateral_offset_distance': 15.0,
#                 'virtual_waypoint_acceptance_radius': 8.0
#             },  # init_kwargs
#             {
#                 'agent_state': create_agent_state_with_pose(x=0.0, y=0.0, heading=np.pi/4),  # 45 degrees toward waypoint
#                 'obstacles_state': ROSObstaclesState(),
#                 'unsafe_set_state': ROSUnsafeSetState(
#                     convex_hull_vertices=Float64MultiArray(
#                         data=np.array(create_intercepting_polygon_points(
#                             agent_pos=(0.0, 0.0),
#                             waypoint_pos=(100.0, 100.0), 
#                             polygon_center=(50.0, 50.0),  # Midway between agent and waypoint
#                             polygon_size=30.0
#                         )).flatten()
#                     )
#                 ),
#                 'waypoints_state': ROSWaypointsState(
#                     current_waypoint=ROSWaypoint(
#                         position=Point(x=100.0, y=100.0, z=0.0), 
#                         acceptance_radius=10.0
#                     )
#                 )
#             },  # state_kwargs
#             {
#                 'waypoints_state': ROSWaypointsState()
#             },  # expected_reset_output
#             'Test with square unsafe set intercepting agent-waypoint path'
#         ),
        
#         # Test 2: Unsafe set closer to agent
#         (
#             {
#                 'longitudinal_offset_distance': 5.0,
#                 'lateral_offset_distance': 20.0,
#                 'virtual_waypoint_acceptance_radius': 12.0
#             },  # init_kwargs
#             {
#                 'agent_state': create_agent_state_with_pose(x=10.0, y=10.0, heading=0.0),  # Facing east
#                 'obstacles_state': ROSObstaclesState(),
#                 'unsafe_set_state': ROSUnsafeSetState(
#                     convex_hull_vertices=Float64MultiArray(
#                         data=np.array(create_intercepting_polygon_points(
#                             agent_pos=(10.0, 10.0),
#                             waypoint_pos=(200.0, 50.0),
#                             polygon_center=(60.0, 30.0),  # Closer to agent
#                             polygon_size=25.0
#                         )).flatten()
#                     )
#                 ),
#                 'waypoints_state': ROSWaypointsState(
#                     current_waypoint=ROSWaypoint(
#                         position=Point(x=200.0, y=50.0, z=0.0), 
#                         acceptance_radius=15.0
#                     )
#                 )
#             },  # state_kwargs
#             {
#                 'waypoints_state': ROSWaypointsState()
#             },  # expected_reset_output
#             'Test with unsafe set closer to agent position'
#         ),
        
#         # Test 3: Diamond-shaped unsafe set
#         (
#             {
#                 'longitudinal_offset_distance': 8.0,
#                 'lateral_offset_distance': 12.0,
#                 'virtual_waypoint_acceptance_radius': 6.0
#             },  # init_kwargs
#             {
#                 'agent_state': create_agent_state_with_pose(x=-20.0, y=-20.0, heading=np.pi/4),
#                 'obstacles_state': ROSObstaclesState(),
#                 'unsafe_set_state': ROSUnsafeSetState(
#                     convex_hull_vertices=Float64MultiArray(
#                         data=np.array([
#                             # Diamond shape intercepting the path
#                             40.0, 30.0,   # right point
#                             30.0, 40.0,   # top point  
#                             20.0, 30.0,   # left point
#                             30.0, 20.0,   # bottom point
#                         ])
#                     )
#                 ),
#                 'waypoints_state': ROSWaypointsState(
#                     current_waypoint=ROSWaypoint(
#                         position=Point(x=80.0, y=80.0, z=0.0), 
#                         acceptance_radius=8.0
#                     )
#                 )
#             },  # state_kwargs
#             {
#                 'waypoints_state': ROSWaypointsState()
#             },  # expected_reset_output
#             'Test with diamond-shaped unsafe set intercepting path'
#         )
#     ]
# )
# def test_generate_virtual_waypoint_reset_comprehensive(init_kwargs: dict, state_kwargs: dict, expected_reset_output: Dict[str, ROSWaypointsState], test_description: str):
#     """
#     Comprehensive test of the virtual waypoint generator reset with intercepting unsafe sets.
#     """
#     print(f"\n{test_description}")
    
#     # Print test setup for debugging
#     agent_state = state_kwargs['agent_state']
#     waypoint = state_kwargs['waypoints_state'].current_waypoint
#     unsafe_vertices:ROSUnsafeSetState = state_kwargs['unsafe_set_state'].convex_hull_vertices.data
    
#     print(f"Agent position: ({agent_state.pose.position.x}, {agent_state.pose.position.y})")
#     print(f"Waypoint position: ({waypoint.position.x}, {waypoint.position.y})")
#     print(f"Unsafe set vertices: {unsafe_vertices}")
    
#     # Create and test the reset
#     reset: ResetABC = GenerateVirtualWaypointReset(**init_kwargs)
#     actual_reset_output: Dict[str, ROSWaypointsState] = reset.__call__(**state_kwargs)

#     print (f"actual reset output: {actual_reset_output}")
    
#     # # Check that a virtual waypoint was created
#     # virtual_waypoints = actual_reset_output['waypoints_state'].virtual_waypoints
#     # assert len(virtual_waypoints) > 0, "No virtual waypoint was generated"
    
#     # # Print the generated virtual waypoint
#     # vwp = virtual_waypoints[0]
#     # print(f"Generated virtual waypoint: ({vwp.position.x:.2f}, {vwp.position.y:.2f})")
#     # print(f"Virtual waypoint acceptance radius: {vwp.acceptance_radius}")
    
#     # # Basic validation that the virtual waypoint is reasonable
#     # assert isinstance(vwp.position.x, float), "Virtual waypoint x should be float"
#     # assert isinstance(vwp.position.y, float), "Virtual waypoint y should be float"
#     # assert vwp.acceptance_radius == init_kwargs['virtual_waypoint_acceptance_radius'], "Acceptance radius mismatch"
    
#     print("✓ Test passed!")
    