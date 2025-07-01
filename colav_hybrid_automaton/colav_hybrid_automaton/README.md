# nodes module

**Note:** Please do not edit the code within these nodes. These are dynamically configurable nodes that will utilize functions
          assigned via the [hybrid_automaton control config](./../../../config/hybrid_automaton_config.yml). Assuming this configuration
          is set up properly and the components such as the guard conditions dynamics and such function and return the correct types
          these nodes will run fine by themselves


- [life cycle manager](./lifecycle_manager_node.py) -  Manages the lifecycle of the hybrid automaton system. It provides an action server to integrate with external applications, enabling system start, stop, and                                                    reset functionalities.
- [transition evaluator](./transition_evaluator_node.py) - Subscribes to the current mode topic published by the Transition Engine. It evaluates guard conditions in real time and publishes boolean outputs for    each transition. These evaluations are configured via the  [`hybrid automaton configuration`](./../../../config/hybrid_automaton_config_sample.yml)
- [transition engine](./transition_engine_node.py) - Manages the current control mode of the hybrid automaton. Based on real-time transition evaluations, it handles mode switching with respect to defined priorities. This node also invokes state reset functions when a transition occurs.
- [state resets server](./state_resets_srv_node.py) - Provides services for resetting continuous system states during mode transitions, ensuring consistent dynamics across hybrid states.
- [dynamics feedback](./dynamic_feedback_node.py) - Generates real-time continuous dynamics for the hybrid automaton. The behavior depends on the current control mode, which determines the associated controller as specified in the configuration file.
- [invariant](): Placeholder for future functionality to enforce control mode invariants. [TODO]