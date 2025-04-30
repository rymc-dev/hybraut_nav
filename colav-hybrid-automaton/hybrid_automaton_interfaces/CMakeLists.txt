cmake_minimum_required(VERSION 3.8)
project(hybrid_automaton_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)

# ADDED dependencies ------------------------------
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# ADDED dependencies END --------------------------
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg//Waypoint.msg"
  "msg/Waypoints.msg"
  "msg/Dynamics.msg"
  "msg/DynamicsUpdate.msg"
  "msg/hybrid_automaton/GuardsStatus.msg"
  "msg/hybrid_automaton/ResetAck.msg"
  "msg/hybrid_automaton/TransitionPending.msg"
  "srv/hybrid_automaton/Reset.srv"
  "srv/hybrid_automaton/StartHybridAutomaton.srv"
  "action/MissionExecutor.action"
  
  DEPENDENCIES geometry_msgs
  DEPENDENCIES nav_msgs
  DEPENDENCIES std_msgs
  DEPENDENCIES builtin_interfaces
)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(your_test_name tests)
endif()

ament_package()

