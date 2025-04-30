cmake_minimum_required(VERSION 3.8)
project(hybrid_automaton_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)

# ADDED dependencies ------------------------------
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(unique_identifier_msgs)
find_package(builtin_interfaces REQUIRED)


# ADDED dependencies END --------------------------
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Waypoint.msg"
  "msg/Waypoints.msg"
  "msg/Dynamics.msg"
  "msg/DynamicsTimer.msg"
  "msg/Mode.msg"
  "msg/Transition.msg"
  "msg/TransitionPending.msg"
  "msg/TransitionTimer.msg"

  "srv/Reset.srv"
  "srv/StartHybridAutomaton.srv"
  "srv/StopHybridAutomaton.srv"

  DEPENDENCIES geometry_msgs nav_msgs std_msgs builtin_interfaces unique_identifier_msgs
)


if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(your_test_name tests)
endif()

ament_package()

