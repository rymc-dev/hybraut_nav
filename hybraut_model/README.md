# Hybraut Model (HM)

This package contains an implementation of the **Hybraut Model (HM)**, a key component of `hybraut_ros2`.  
The HM is a passive entity — a static representation of a hybrid automaton — which can be utilized within the `hybraut_ros2` package.  
It contains a hierarchical representation of an automaton that matches the formal mathematical definition as closely as possible.  

The HM models the **high-level design** of the automaton.  
For the **lower-level components** of the automaton — guards, resets, dynamics, and invariants — it uses wrappers for implementations from `hybraut_aci`.  
These implementations allow the components to operate within the Hybraut architecture while adhering to the defined automaton rules.  

This standardized layout also enables the use of a custom-built DSL called **AMDL** (Automaton Model Definition Language), a formal language for encoding automata mathematically and integrating them into the Hybraut framework.  
Accordingly, there are class functions for the hybrid automaton that allow you to pass in an AMDL YAML dictionary to initialize an instance of `HybridAutomaton`.
