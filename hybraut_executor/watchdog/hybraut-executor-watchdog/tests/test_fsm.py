#!/usr/bin/python3
# -*- coding: utf-8  -*-
"""
Test suite for the Enhanced Hybraut Watchdog Finite State Machine (FSM)

This test suite provides comprehensive coverage for:
- State transitions and their validity
- Event handling and trigger mapping
- Callback execution and error handling
- Hook system functionality
- Custom FSM subclass behavior
- Error recovery mechanisms
- ROS 2 integration components
"""

# import unittest
# from unittest.mock import Mock, MagicMock, patch, call
# import pytest
# from typing import Any

# # Mock ROS 2 imports before importing the FSM module
# import sys
# from unittest.mock import MagicMock

# # Create mock modules
# mock_rclpy = MagicMock()
# mock_rclpy.node = MagicMock()
# mock_rclpy.publisher = MagicMock()
# mock_rclpy.impl.rcutils_logger = MagicMock()
# mock_rclpy.qos = MagicMock()
# mock_rclpy.callback_groups = MagicMock()
# mock_builtin_interfaces = MagicMock()
# mock_hybraut_interfaces = MagicMock()
# mock_hybraut_executor_watchdog = MagicMock()

# # Add mocks to sys.modules
# sys.modules['rclpy'] = mock_rclpy
# sys.modules['rclpy.node'] = mock_rclpy.node
# sys.modules['rclpy.publisher'] = mock_rclpy.publisher
# sys.modules['rclpy.impl'] = mock_rclpy.impl
# sys.modules['rclpy.impl.rcutils_logger'] = mock_rclpy.impl.rcutils_logger
# sys.modules['rclpy.qos'] = mock_rclpy.qos
# sys.modules['rclpy.callback_groups'] = mock_rclpy.callback_groups
# sys.modules['builtin_interfaces'] = mock_builtin_interfaces
# sys.modules['builtin_interfaces.msg'] = mock_builtin_interfaces.msg
# sys.modules['hybraut_interfaces'] = mock_hybraut_interfaces
# sys.modules['hybraut_interfaces.msg'] = mock_hybraut_interfaces.msg
# sys.modules['hybraut_executor_watchdog'] = mock_hybraut_executor_watchdog
# sys.modules['hybraut_executor_watchdog.hybraut_consts'] = mock_hybraut_executor_watchdog.hybraut_consts
# sys.modules['hybraut_executor_watchdog.hybraut_bus'] = mock_hybraut_executor_watchdog.hybraut_bus

# # Mock the enums and classes we need
# from enum import Enum

# class MockStatusEnum(Enum):
#     ACTIVE = "active"
#     TRANSITIONING = "transitioning"
#     ERROR = "error"
#     RECOVERING = "recovering"
#     MISSION_COMPLETE = "mission_complete"
#     FATAL = "fatal"

# class MockEventEnum(Enum):
#     VALID_MISSION_REQUEST = "valid_mission_request"
#     TRANSITION_GUARD_ENABLED = "transition_guard_enabled"
#     TRANSITION_COMPLETE = "transition_complete"
#     RECOVERABLE_ERROR = "recoverable_error"
#     ATTEMPT_FIX = "attempt_fix"
#     RECOVERED = "recovered"
#     RECOVERY_FAILED = "recovery_failed"
#     CRITICAL_FAILURE = "critical_failure"
#     MISSION_COMPLETE = "mission_complete"
#     SHUTDOWN = "shutdown"

# # Set up the mock enums
# mock_hybraut_executor_watchdog.hybraut_consts.StatusEnum = MockStatusEnum
# mock_hybraut_executor_watchdog.hybraut_consts.EventEnum = MockEventEnum

# # Mock message classes
# class MockAutomatonEvents:
#     def __init__(self, type=None, message=""):
#         self.type = type
#         self.message = message

# class MockAutomatonStatus:
#     def __init__(self, status=None, message=""):
#         self.status = status
#         self.message = message

# mock_hybraut_interfaces.msg.AutomatonEvents = MockAutomatonEvents
# mock_hybraut_interfaces.msg.AutomatonStatus = MockAutomatonStatus

# # Mock bus classes
# class MockStatusBus:
#     def __init__(self, node, status_callback, cb_group=None, qos=None):
#         self.node = node
#         self.status_callback = status_callback
#         self.cb_group = cb_group
#         self.qos = qos
        
#     def publish(self, data, message=""):
#         pass

# class MockEventBus:
#     def __init__(self, node, event_callback, cb_group=None, qos=None):
#         self.node = node
#         self.event_callback = event_callback
#         self.cb_group = cb_group
#         self.qos = qos

# mock_hybraut_executor_watchdog.hybraut_bus.StatusBus = MockStatusBus
# mock_hybraut_executor_watchdog.hybraut_bus.EventBus = MockEventBus

# # Now import the FSM classes (this should be done after mocking)
# # For this test, we'll define simplified versions of the classes to test
# from transitions import Machine

# class TestFSM:
#     """Test version of FSM class with simplified dependencies"""
    
#     states = [status for status in MockStatusEnum]
    
#     transition_function_map = {
#         MockEventEnum.VALID_MISSION_REQUEST: "activate_mission",
#         MockEventEnum.TRANSITION_GUARD_ENABLED: "enable_guard",
#         MockEventEnum.TRANSITION_COMPLETE: "complete_transition",
#         MockEventEnum.RECOVERABLE_ERROR: "handle_recoverable_error",
#         MockEventEnum.ATTEMPT_FIX: "attempt_fix_process",
#         MockEventEnum.RECOVERED: "complete_recovery",
#         MockEventEnum.RECOVERY_FAILED: "fail_recovery",
#         MockEventEnum.CRITICAL_FAILURE: "handle_critical_failure",
#         MockEventEnum.MISSION_COMPLETE: "finish_mission",
#         MockEventEnum.SHUTDOWN: "shutdown_system",
#     }

#     def __init__(self, node=None, cb_group=None, qos=None, initial_state=MockStatusEnum.ACTIVE):
#         # Mock node if not provided
#         if node is None:
#             node = Mock()
#             node.get_logger.return_value = Mock()
        
#         self.node = node
#         self.cb_group = cb_group or Mock()
#         self.qos = qos or Mock()
        
#         # Initialize state machine
#         self.machine = Machine(
#             model=self,
#             states=self.states,
#             initial=initial_state,
#             after_state_change=lambda event: self.publish_status(event),
#             ignore_invalid_triggers=True,
#         )
#         self._add_transitions()
#         self.__post_init__(node=node, cb_group=cb_group, qos=qos)

#     def _add_transitions(self):
#         """Add all state transitions with their callback handlers."""
#         # Normal operational flow
#         self.machine.add_transition(
#             trigger="enable_guard",
#             source=MockStatusEnum.ACTIVE,
#             dest=MockStatusEnum.TRANSITIONING,
#             after=self._safe_callback_wrapper("on_guard_enabled")
#         )
#         self.machine.add_transition(
#             trigger="complete_transition",
#             source=MockStatusEnum.TRANSITIONING,
#             dest=MockStatusEnum.ACTIVE,
#             after=self._safe_callback_wrapper("on_transition_complete")
#         )
#         self.machine.add_transition(
#             trigger="finish_mission",
#             source=MockStatusEnum.ACTIVE,
#             dest=MockStatusEnum.MISSION_COMPLETE,
#             after=self._safe_callback_wrapper("on_mission_complete")
#         )

#         # Error handling
#         self.machine.add_transition(
#             trigger="handle_recoverable_error",
#             source=[MockStatusEnum.ACTIVE, MockStatusEnum.TRANSITIONING],
#             dest=MockStatusEnum.ERROR,
#             after=self._safe_callback_wrapper("on_recoverable_error")
#         )
#         self.machine.add_transition(
#             trigger="attempt_fix_process",
#             source=MockStatusEnum.ERROR,
#             dest=MockStatusEnum.RECOVERING,
#             after=self._safe_callback_wrapper("on_attempt_fix")
#         )
#         self.machine.add_transition(
#             trigger="complete_recovery",
#             source=MockStatusEnum.RECOVERING,
#             dest=MockStatusEnum.ACTIVE,
#             after=self._safe_callback_wrapper("on_recovered")
#         )
#         self.machine.add_transition(
#             trigger="fail_recovery",
#             source=MockStatusEnum.RECOVERING,
#             dest=MockStatusEnum.ERROR,
#             after=self._safe_callback_wrapper("on_recovery_failed")
#         )
#         self.machine.add_transition(
#             trigger="handle_critical_failure",
#             source=[MockStatusEnum.ERROR, MockStatusEnum.RECOVERING],
#             dest=MockStatusEnum.FATAL,
#             after=self._safe_callback_wrapper("on_critical_failure")
#         )

#         # Shutdown from any non-fatal state
#         for state in MockStatusEnum:
#             if state != MockStatusEnum.FATAL:
#                 self.machine.add_transition(
#                     trigger="shutdown_system",
#                     source=state,
#                     dest=MockStatusEnum.FATAL,
#                     after=self._safe_callback_wrapper("on_shutdown")
#                 )

#     def _safe_callback_wrapper(self, callback_name: str):
#         """Creates a safe wrapper for callback functions."""
#         def wrapper(event):
#             try:
#                 callback_method = getattr(self, callback_name, None)
#                 if callback_method and callable(callback_method):
#                     callback_method(event)
#                 else:
#                     self.node.get_logger().warning(
#                         f"Callback {callback_name} not found or not callable"
#                     )
#             except Exception as e:
#                 self.node.get_logger().error(
#                     f"Error in callback {callback_name}: {e}"
#                 )
#         return wrapper

#     def __post_init__(self, node, cb_group=None, qos=None):
#         self.status_bus = MockStatusBus(
#             node=node,
#             status_callback=self.status_callback,
#             cb_group=cb_group,
#             qos=qos
#         )
#         self.event_bus = MockEventBus(
#             node=node,
#             event_callback=self.trigger_transition,
#             cb_group=cb_group,
#             qos=qos,
#         )

#     def status_callback(self, msg):
#         """Handle incoming status messages."""
#         self.node.get_logger().info(f"Status received: {msg}")

#     def publish_status(self, event):
#         """Publish status updates."""
#         try:
#             self.status_bus.publish(
#                 data=self.get_current_state(),
#                 message=f"State changed to {self.get_current_state()}",
#             )
#             self.node.get_logger().info(f"Published status: {self.get_current_state()}")
#         except Exception as e:
#             self.node.get_logger().error(f"Failed to publish status: {e}")

#     def trigger_transition(self, event):
#         """Process incoming events and trigger appropriate transitions."""
#         if not isinstance(event, MockAutomatonEvents):
#             self.node.get_logger().error(f"Invalid event type: {type(event)}")
#             return
        
#         enum_dict = {enum.value: enum for enum in MockEventEnum}
#         if event.type not in enum_dict:
#             self.node.get_logger().warn(f"Unknown event: {event.type}")
#             return
        
#         event_enum = enum_dict[event.type]
#         self.node.get_logger().info(f"Processing event: {event_enum}")
#         self.perform_event_driven_transition(event_enum)

#     def perform_event_driven_transition(self, event):
#         """Execute the appropriate transition for the given event."""
#         trigger = self.transition_function_map.get(event)
#         if not trigger:
#             raise ValueError(f"No trigger mapped for event {event}")
#         if not hasattr(self, trigger):
#             raise AttributeError(f"Trigger method {trigger} not found")
#         getattr(self, trigger)(event)
#         self.node.get_logger().info(f"Fired trigger: {trigger}")

#     def get_current_state(self):
#         """Get the current state of the FSM."""
#         return self.state

#     def get_valid_transitions(self):
#         """Get list of valid transitions from current state."""
#         return self.machine.get_triggers(self.state)

#     def is_terminal_state(self):
#         """Check if current state is terminal (FATAL)."""
#         return self.state == MockStatusEnum.FATAL

#     def _call_hook(self, hook_name: str, event):
#         """Call a hook method if it exists."""
#         hook_method = getattr(self, hook_name, None)
#         if hook_method and callable(hook_method):
#             try:
#                 hook_method(event)
#             except Exception as e:
#                 self.node.get_logger().error(f"Error in hook {hook_name}: {e}")

#     # Default callback implementations
#     def on_guard_enabled(self, event):
#         self.node.get_logger().info(f"Guard enabled, transitioning: {event}")
#         self._call_hook("pre_guard_enabled", event)
#         self._execute_guard_enabled_logic(event)
#         self._call_hook("post_guard_enabled", event)

#     def on_transition_complete(self, event):
#         self.node.get_logger().info(f"Transition complete: {event}")
#         self._call_hook("pre_transition_complete", event)
#         self._execute_transition_complete_logic(event)
#         self._call_hook("post_transition_complete", event)

#     def on_mission_complete(self, event):
#         self.node.get_logger().info("Mission completed successfully")
#         self._call_hook("pre_mission_complete", event)
#         self._execute_mission_complete_logic(event)
#         self._call_hook("post_mission_complete", event)

#     def on_recoverable_error(self, event):
#         self.node.get_logger().warning("Entered ERROR state")
#         self._call_hook("pre_recoverable_error", event)
#         self._execute_recoverable_error_logic(event)
#         self._call_hook("post_recoverable_error", event)

#     def on_attempt_fix(self, event):
#         self.node.get_logger().info("Attempting to recover from error")
#         self._call_hook("pre_attempt_fix", event)
#         self._execute_attempt_fix_logic(event)
#         self._call_hook("post_attempt_fix", event)

#     def on_recovered(self, event):
#         self.node.get_logger().info("Recovery successful, back to ACTIVE")
#         self._call_hook("pre_recovered", event)
#         self._execute_recovered_logic(event)
#         self._call_hook("post_recovered", event)

#     def on_recovery_failed(self, event):
#         self.node.get_logger().error("Recovery attempt failed, back in ERROR")
#         self._call_hook("pre_recovery_failed", event)
#         self._execute_recovery_failed_logic(event)
#         self._call_hook("post_recovery_failed", event)

#     def on_critical_failure(self, event):
#         self.node.get_logger().fatal("Critical failure: entering FATAL state")
#         self._call_hook("pre_critical_failure", event)
#         self._execute_critical_failure_logic(event)
#         self._call_hook("post_critical_failure", event)

#     def on_shutdown(self, event):
#         self.node.get_logger().info("Shutdown initiated: entering FATAL state")
#         self._call_hook("pre_shutdown", event)
#         self._execute_shutdown_logic(event)
#         self._call_hook("post_shutdown", event)

#     # Base implementation methods (can be overridden)
#     def _execute_guard_enabled_logic(self, event): pass
#     def _execute_transition_complete_logic(self, event): pass
#     def _execute_mission_complete_logic(self, event): pass
#     def _execute_recoverable_error_logic(self, event): pass
#     def _execute_attempt_fix_logic(self, event): pass
#     def _execute_recovered_logic(self, event): pass
#     def _execute_recovery_failed_logic(self, event): pass
#     def _execute_critical_failure_logic(self, event): pass
#     def _execute_shutdown_logic(self, event): pass


# class TestCustomFSM(TestFSM):
#     """Test version of CustomFSM with tracking capabilities"""
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.error_count = 0
#         self.recovery_attempts = 0
#         self.hook_calls = []

#     def on_recoverable_error(self, event):
#         """Override to add error tracking."""
#         super().on_recoverable_error(event)
#         self.error_count += 1
#         self.node.get_logger().info(f"Total errors encountered: {self.error_count}")

#     def on_attempt_fix(self, event):
#         """Override to add recovery attempt tracking."""
#         super().on_attempt_fix(event)
#         self.recovery_attempts += 1
#         self.node.get_logger().info(f"Recovery attempt #{self.recovery_attempts}")

#     def pre_guard_enabled(self, event):
#         """Hook called before guard enabled logic."""
#         self.hook_calls.append("pre_guard_enabled")
#         self.node.get_logger().info("Preparing for guard activation...")

#     def post_mission_complete(self, event):
#         """Hook called after mission complete logic."""
#         self.hook_calls.append("post_mission_complete")
#         self.node.get_logger().info(f"Mission statistics: {self.error_count} errors, {self.recovery_attempts} recoveries")


# # =============================================================================
# # TEST CLASSES
# # =============================================================================

# class TestFSMBasicFunctionality(unittest.TestCase):
#     """Test basic FSM functionality including initialization and state management."""

#     def setUp(self):
#         """Set up test fixtures."""
#         self.mock_node = Mock()
#         self.mock_logger = Mock()
#         self.mock_node.get_logger.return_value = self.mock_logger
#         self.fsm = TestFSM(node=self.mock_node)

#     def test_initialization(self):
#         """Test FSM initialization with default parameters."""
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.ACTIVE)
#         self.assertIsNotNone(self.fsm.machine)
#         self.assertIsNotNone(self.fsm.status_bus)
#         self.assertIsNotNone(self.fsm.event_bus)

#     def test_initialization_with_custom_initial_state(self):
#         """Test FSM initialization with custom initial state."""
#         fsm = TestFSM(node=self.mock_node, initial_state=MockStatusEnum.ERROR)
#         self.assertEqual(fsm.get_current_state(), MockStatusEnum.ERROR)

#     def test_get_valid_transitions(self):
#         """Test getting valid transitions from current state."""
#         transitions = self.fsm.get_valid_transitions()
#         self.assertIsInstance(transitions, list)
#         self.assertIn('enable_guard', transitions)
#         self.assertIn('handle_recoverable_error', transitions)

#     def test_is_terminal_state(self):
#         """Test terminal state detection."""
#         self.assertFalse(self.fsm.is_terminal_state())
        
#         # Trigger shutdown to reach terminal state
#         self.fsm.shutdown_system(MockEventEnum.SHUTDOWN)
#         self.assertTrue(self.fsm.is_terminal_state())


# class TestFSMStateTransitions(unittest.TestCase):
#     """Test state transitions and their validity."""

#     def setUp(self):
#         """Set up test fixtures."""
#         self.mock_node = Mock()
#         self.mock_logger = Mock()
#         self.mock_node.get_logger.return_value = self.mock_logger
#         self.fsm = TestFSM(node=self.mock_node)

#     def test_normal_operational_flow(self):
#         """Test normal operational state transitions."""
#         # Start in ACTIVE state
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.ACTIVE)
        
#         # Transition to TRANSITIONING
#         self.fsm.enable_guard(MockEventEnum.TRANSITION_GUARD_ENABLED)
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.TRANSITIONING)
        
#         # Complete transition back to ACTIVE
#         self.fsm.complete_transition(MockEventEnum.TRANSITION_COMPLETE)
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.ACTIVE)
        
#         # Complete mission
#         self.fsm.finish_mission(MockEventEnum.MISSION_COMPLETE)
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.MISSION_COMPLETE)

#     def test_error_handling_flow(self):
#         """Test error handling state transitions."""
#         # Start in ACTIVE state
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.ACTIVE)
        
#         # Trigger recoverable error
#         self.fsm.handle_recoverable_error(MockEventEnum.RECOVERABLE_ERROR)
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.ERROR)
        
#         # Attempt recovery
#         self.fsm.attempt_fix_process(MockEventEnum.ATTEMPT_FIX)
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.RECOVERING)
        
#         # Successful recovery
#         self.fsm.complete_recovery(MockEventEnum.RECOVERED)
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.ACTIVE)

#     def test_failed_recovery_flow(self):
#         """Test failed recovery scenario."""
#         # Get to ERROR state
#         self.fsm.handle_recoverable_error(MockEventEnum.RECOVERABLE_ERROR)
#         self.fsm.attempt_fix_process(MockEventEnum.ATTEMPT_FIX)
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.RECOVERING)
        
#         # Fail recovery
#         self.fsm.fail_recovery(MockEventEnum.RECOVERY_FAILED)
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.ERROR)

#     def test_critical_failure_from_error(self):
#         """Test critical failure from ERROR state."""
#         # Get to ERROR state
#         self.fsm.handle_recoverable_error(MockEventEnum.RECOVERABLE_ERROR)
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.ERROR)
        
#         # Trigger critical failure
#         self.fsm.handle_critical_failure(MockEventEnum.CRITICAL_FAILURE)
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.FATAL)

#     def test_shutdown_from_various_states(self):
#         """Test shutdown capability from different states."""
#         states_to_test = [
#             MockStatusEnum.ACTIVE,
#             MockStatusEnum.TRANSITIONING,
#             MockStatusEnum.ERROR,
#             MockStatusEnum.RECOVERING,
#             MockStatusEnum.MISSION_COMPLETE
#         ]
        
#         for initial_state in states_to_test:
#             with self.subTest(initial_state=initial_state):
#                 fsm = TestFSM(node=self.mock_node, initial_state=initial_state)
#                 fsm.shutdown_system(MockEventEnum.SHUTDOWN)
#                 self.assertEqual(fsm.get_current_state(), MockStatusEnum.FATAL)


# class TestFSMEventHandling(unittest.TestCase):
#     """Test event handling and trigger mapping."""

#     def setUp(self):
#         """Set up test fixtures."""
#         self.mock_node = Mock()
#         self.mock_logger = Mock()
#         self.mock_node.get_logger.return_value = self.mock_logger
#         self.fsm = TestFSM(node=self.mock_node)

#     def test_trigger_transition_valid_event(self):
#         """Test triggering transition with valid event."""
#         event = MockAutomatonEvents(
#             type=MockEventEnum.TRANSITION_GUARD_ENABLED.value,
#             message="Test message"
#         )
        
#         self.fsm.trigger_transition(event)
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.TRANSITIONING)

#     def test_trigger_transition_invalid_event_type(self):
#         """Test triggering transition with invalid event type."""
#         invalid_event = "not an event"
        
#         self.fsm.trigger_transition(invalid_event)
        
#         # Should log error and not change state
#         self.mock_logger.error.assert_called()
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.ACTIVE)

#     def test_trigger_transition_unknown_event(self):
#         """Test triggering transition with unknown event type."""
#         event = MockAutomatonEvents(type="unknown_event", message="Test")
        
#         self.fsm.trigger_transition(event)
        
#         # Should log warning and not change state
#         self.mock_logger.warn.assert_called()
#         self.assertEqual(self.fsm.get_current_state(), MockStatusEnum.ACTIVE)

#     def test_perform_event_driven_transition_invalid_event(self):
#         """Test perform_event_driven_transition with invalid event."""
#         # Create a mock event not in transition_function_map
#         class MockInvalidEvent(Enum):
#             INVALID = "invalid"
        
#         with self.assertRaises(ValueError):
#             self.fsm.perform_event_driven_transition(MockInvalidEvent.INVALID)

#     def test_transition_function_map_completeness(self):
#         """Test that all events have corresponding trigger functions."""
#         for event, trigger in self.fsm.transition_function_map.items():
#             with self.subTest(event=event, trigger=trigger):
#                 self.assertTrue(hasattr(self.fsm, trigger),
#                               f"FSM missing trigger method: {trigger}")


# class TestFSMCallbackHandling(unittest.TestCase):
#     """Test callback execution and error handling."""

#     def setUp(self):
#         """Set up test fixtures."""
#         self.mock_node = Mock()
#         self.mock_logger = Mock()
#         self.mock_node.get_logger.return_value = self.mock_logger
#         self.fsm = TestFSM(node=self.mock_node)

#     def test_safe_callback_wrapper_success(self):
#         """Test successful callback execution."""
#         test_event = MockEventEnum.TRANSITION_GUARD_ENABLED
        
#         # Mock the callback method
#         self.fsm.on_guard_enabled = Mock()
        
#         # Get the wrapper and call it
#         wrapper = self.fsm._safe_callback_wrapper("on_guard_enabled")
#         wrapper(test_event)
        
#         # Verify callback was called
#         self.fsm.on_guard_enabled.assert_called_once_with(test_event)

#     def test_safe_callback_wrapper_missing_callback(self):
#         """Test callback wrapper with missing callback method."""
#         test_event = MockEventEnum.TRANSITION_GUARD_ENABLED
        
#         # Ensure callback doesn't exist
#         if hasattr(self.fsm, 'nonexistent_callback'):
#             delattr(self.fsm, 'nonexistent_callback')
        
#         wrapper = self.fsm._safe_callback_wrapper("nonexistent_callback")
#         wrapper(test_event)
        
#         # Should log warning about missing callback
#         self.mock_logger.warning.assert_called()

#     def test_safe_callback_wrapper_callback_exception(self):
#         """Test callback wrapper handling callback exceptions."""
#         test_event = MockEventEnum.TRANSITION_GUARD_ENABLED
        
#         # Mock callback that raises exception
#         def failing_callback(event):
#             raise ValueError("Test exception")
        
#         self.fsm.on_guard_enabled = failing_callback
        
#         wrapper = self.fsm._safe_callback_wrapper("on_guard_enabled")
#         wrapper(test_event)
        
#         # Should log error about callback exception
#         self.mock_logger.error.assert_called()

#     def test_callback_execution_during_transition(self):
#         """Test that callbacks are executed during state transitions."""
#         # Mock all callback methods
#         self.fsm.on_guard_enabled = Mock()
        
#         # Trigger transition
#         self.fsm.enable_guard(MockEventEnum.TRANSITION_GUARD_ENABLED)
        
#         # Verify callback was called
#         self.fsm.on_guard_enabled.assert_called_once()


# class TestFSMHookSystem(unittest.TestCase):
#     """Test the hook system functionality."""

#     def setUp(self):
#         """Set up test fixtures."""
#         self.mock_node = Mock()
#         self.mock_logger = Mock()
#         self.mock_node.get_logger.return_value = self.mock_logger
#         self.fsm = TestFSM(node=self.mock_node)

#     def test_call_hook_existing_hook(self):
#         """Test calling an existing hook method."""
#         test_event = MockEventEnum.TRANSITION_GUARD_ENABLED
        
#         # Add a mock hook method
#         self.fsm.test_hook = Mock()
        
#         self.fsm._call_hook("test_hook", test_event)
        
#         # Verify hook was called
#         self.fsm.test_hook.assert_called_once_with(test_event)

#     def test_call_hook_nonexistent_hook(self):
#         """Test calling a non-existent hook method."""
#         test_event = MockEventEnum.TRANSITION_GUARD_ENABLED
        
#         # This should not raise an exception
#         self.fsm._call_hook("nonexistent_hook", test_event)
        
#         # No error should be logged for missing hooks
#         self.mock_logger.error.assert_not_called()

#     def test_call_hook_exception_handling(self):
#         """Test hook exception handling."""
#         test_event = MockEventEnum.TRANSITION_GUARD_ENABLED
        
#         def failing_hook(event):
#             raise RuntimeError("Hook failed")
        
#         self.fsm.test_hook = failing_hook
        
#         self.fsm._call_hook("test_hook", test_event)
        
#         # Should log error about hook exception
#         self.mock_logger.error.assert_called()

#     def test_hooks_called_in_callback(self):
#         """Test that hooks are called during callback execution."""
#         test_event = MockEventEnum.TRANSITION_GUARD_ENABLED