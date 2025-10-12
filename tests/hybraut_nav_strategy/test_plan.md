# **Test Plan — `StrategyNode`**

This document defines the unit test scenarios for `StrategyNode`, which is the key 
interface for Layer1 the `strategy layer` of the HybrautNav system which is a three layer hybrid control system tactical navigation of dyanmic environemnts. 

## **goal_received_callback**

This Part defines the unit test scenarios positive and negative for the `goal_Receive_callback`, a callback function for when the `hybraut_nav/send_goal` service is called. 

### **Test Scenarios**

| **Test ID** | **Scenario** | **Preconditions / Inputs** | **Expected Outputs** |
|--------------|--------------|-----------------------------|-----------------------|
| **T1** | **Valid Send Goal Request** | - `internal world state variables have values, map has valid occupancy grid, agent_state have valid agent state` <br> - `internal state should be == 'INACTIVE'` | - `Should Toggle internal state to active` <br> - `Should initialize a subscription to hybraut_nav/vw` <br> - `Should enable replan_timer` | <br> - `an initialial valid plan should be published` |
| **T2** | **Inavlid SendGoalRequest (no world state presence)** | | | | 
| **T3** | **Inavlid SendGoal Request (request pose type is invalid)** | | | 
| **T4** | **Invalid SendGoal Request (Frame on map state varaible and goal pose state variable are not the same)** | | | | 
| **T5** | **Invalid SendGoal Request (GoalPose outside map bounds)** | | | | 
| **T6** | ** 


---

## **cancel_goal_callback**

This section defines the tests for `cancal_goal_callback` a callback function for the `cancel_goal` service. 
---

### **Test Scenarios**

| **Test ID** | **Scenario** | **Preconditions / Inputs** | **Expected Outputs** |
|--------------|--------------|-----------------------------|-----------------------|
| **T1** | **Valid Cancel Request** | - `state = StrategyState.ACTIVE`<br>- `replan_timer` is active | - `state` transitions to `StrategyState.INACTIVE`<br>- `replan_timer` remains available but inactive<br>- `goal_pose` and `vw` reset to `None`<br>- Callback returns success response |
| **T2** | **Invalid Cancel Request (Already Inactive)** | - `state = StrategyState.INACTIVE` | - Node remains `INACTIVE`<br>- Callback returns failure response with reason `"No active goal to cancel"` (or equivalent)<br>- No changes to `replan_timer` or goal-related variables |
| **T3** | **Edge Case — Timer Missing or Inactive** | - `state = StrategyState.ACTIVE`<br>- `replan_timer = None` or inactive | - Function returns `False` (or error response)<br>- Log or message indicates `"Timer not active"` exception<br>- `state` transitions to `StrategyState.INACTIVE` for consistency |
---


## **get_replan_frequency**

Test for the getter function `get_replan_frequency`

### **Test Scenarios**

---

## **get_planner_type**
Test for the getter function `get_planner_type`

### **Test Scenarios**

---

## **get_max_planning_time**
Test for the getter function `get_map_planning_time`

### **Test Scenarios**

---

## **get_description**
Test the for the getter function `get_description`


### **Test Scenarios**

---

## **get_state**
Test for the getter function `get_state`

### **Test Scenarios**

---

## **set_planner**
Test for the setter function `set_planner`

### **Test Scenarios**

--- 

## **set_replan_frequency**
Ttest for the setter function `set_replan_frequency`

### **Test Scenarios**

--- 

## **set_max_planning_time**
Test for the setter function `set_max_planning_time`

### **Test Scenarios**

--- 

## **toggle_state** 
Test for helper function for toggling internal state of the `StrategyNode`

### **Test Scenarios**

--- 

## **publish_path**
Test for the helper function for publishing a path utilizing an internal publisher `publish_path` 

### **Test Scenarios**

--- 

## **map_callback**
Test for the callback function `map_callback` which is called on `map_sub` receive of a `OccupancyMap` it will do simple validation of the occupancy grid and convert it from the ROS message to a message that can be utilized by the Planner Classes then this will store the map attribute. 

### **Test Scenarios**

--- 

## **agent_state_callback**
Test for the callback function `agent_state_callback` which is called on `agent_sub` receive of a new state update, This will do simple verification of the data contained and extract Point which the state is and convert this point to something that can be used by the planner classes.

### **Test Scenarios**

--- 


## **virtual_waypoint_callback**
virtual waypoints are only published by the tactical layer of the HybrautNav stack. This is in response to some form of tactical decision whether that be avoiding a region due to environemntal issues or something else. Therefore we should validate this virtual waypoint against the map global state attribute currently, and then make a new global plan which generates a path to virtual waypoint then goal waypoint is possible.  

### **Test Scenarios**

--- 


## **replan_callback** 

This section defines a test suite for the `replan_callback` function which is the function called on timer click for the `replan_timer` in this node.

### **Test Scenarios**
| **Test ID** | **Scenario** | **Preconditions / Inputs** | **Expected Outputs** |
|--------------|--------------|-----------------------------|-----------------------|
| T1 | | | | |
| T2 | | | | |
| T3 | | | | | 

--- 


## **parameter callback** 

This section dedines test cases for the `parameter_callback` which is a function for dynamic configuration of parameters of this node. It handles parameter change requests taking care of proper exception handling in case something is wrong.

### **Test Scenarios** 

... 

--- 


## **deactivate_replan_timer** 

### **Test Scenarios** 

--- 

## **activate_replan_timer** 

### **Test Scenarios

--- 


## **Additional Notes**
- Use mocks for ROS timers and service requests to simulate different node states.  
- Assert all expected **side effects**, such as variable resets and state transitions.  
- Verify exception handling and logging for the edge case scenario.
