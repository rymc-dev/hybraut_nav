cmake_minimum_required(VERSION 3.8)
project(hybraut_nav)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(unique_identifier_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)

# ---------------------------------------------------------------------------
# 1. Interface generation (formerly hybraut_interfaces/CMakeLists.txt +
#    colav_interfaces/CMakeLists.txt, moved in unchanged under
#    PROJECT_NAME=hybraut_nav so generated types become
#    hybraut_nav/action/ExecuteMission, hybraut_nav/msg/Waypoint, etc.)
#
#    NOTE: rosidl_generate_interfaces() internally calls
#    ament_python_install_package(hybraut_nav PACKAGE_DIR <generated dir>)
#    on our behalf. Do NOT call ament_python_install_package(hybraut_nav)
#    again anywhere else in this file - see the plain install(DIRECTORY ...)
#    below for the hand-written hybraut_nav/ python package instead.
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/agent_state/AgentState.msg"

  "msg/obstacles_state/dynamic_obstacle/DynamicObstacleGeometry.msg"
  "msg/obstacles_state/dynamic_obstacle/DynamicObstacleState.msg"

  "msg/obstacles_state/static_obstacle/StaticObstacleGeometry.msg"
  "msg/obstacles_state/static_obstacle/StaticObstacleState.msg"

  "msg/obstacles_state/ObstaclesState.msg"

  "msg/waypoints_state/Waypoint.msg"

  "action/ExecuteMission.action"
  "action/NavigateToGoal.action"
  DEPENDENCIES geometry_msgs nav_msgs std_msgs builtin_interfaces unique_identifier_msgs
)

# ---------------------------------------------------------------------------
# 2. Hand-written Python code (formerly installed via setup.py's
#    find_packages()). hybraut_nav/ (the top-level plain-python package:
#    qos/, scripts/, state/) is installed manually here, NOT via
#    ament_python_install_package(), since that name collides with
#    PROJECT_NAME (already registered above by rosidl_generate_interfaces).
#    Both trees' __init__.py are empty, and their subdirectories are
#    disjoint (msg/srv/action vs qos/scripts/state), so they merge cleanly
#    as siblings on disk.
install(
  DIRECTORY hybraut_nav/
  DESTINATION ${PYTHON_INSTALL_DIR}/hybraut_nav
  PATTERN "*.pyc" EXCLUDE
  PATTERN "__pycache__" EXCLUDE
)

ament_python_install_package(hybraut_nav_strategy)
ament_python_install_package(hybraut_nav_immediate)
ament_python_install_package(hybraut_nav_tactical)
ament_python_install_package(hybraut_nav_risk)
ament_python_install_package(hybraut_nav_utils)

# ---------------------------------------------------------------------------
# 3. Console-script replacements (formerly setup.py entry_points - inert
#    once build_type is ament_cmake, colcon never runs setup.py at all).
install(PROGRAMS
  scripts/strategy_node
  scripts/immediate_node
  scripts/tactical_node
  scripts/risk_envelope_node
  scripts/fake_riskenv_publisher
  scripts/colreg_encounter_publisher
  scripts/fake_map_publisher
  scripts/mover_random_walk
  scripts/agent_state_bridge
  scripts/obstacles_state_bridge
  DESTINATION lib/${PROJECT_NAME}
)

# ---------------------------------------------------------------------------
# 4. share/ data files (formerly setup.py data_files). package.xml and the
#    ament-index resource-index marker are installed automatically by
#    ament_package() for ament_cmake packages.
install(DIRECTORY launch/ DESTINATION share/${PROJECT_NAME}/launch FILES_MATCHING PATTERN "*.launch.py")
install(DIRECTORY worlds/models/simple_mover/ DESTINATION share/${PROJECT_NAME}/worlds/models/simple_mover FILES_MATCHING PATTERN "*.sdf")
install(DIRECTORY rviz/ DESTINATION share/${PROJECT_NAME}/rviz FILES_MATCHING PATTERN "*.rviz")

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(hybraut_nav_pytest tests)
endif()

ament_package()
