# Automaton Component Interfaces (`aci`)

Automaton Component Interfaces are **blueprints** for creating low-level components—such as **Guards**, **Resets**, **Dynamics**, and **Invariants**—that plug seamlessly into the hybrid automaton framework.  

You can implement these interfaces in your own Python package, then reference them in your `amdl` formal definition by specifying the module and class name.  
If the interface contract is implemented correctly, your custom component will integrate automatically during both:  
- **Initialization** (`amdl` → Hybrid Model `hm`)  
- **Activation** (Hybrid Model `hm` → Hybrid Execution Engine `hee`)  

---

## How it Works

### Architecture
An `aci` follows a consistent **two-phase lifecycle**:

1. **Initialization Phase**
   - The class is instantiated with `init_kwargs` defined in the `amdl` specification.
   - Required parameters are validated.
   - Component is prepared with all needed configuration.

2. **Runtime Phase**
   - When the automaton activates, the component becomes callable.
   - Current state values are passed to its `__call__` method.
   - The component logic processes the inputs and produces outputs according to its spec.

---

### Execution Flow
1. **Linking** – `amdl` file references a specific `aci` class.
2. **Initialization** – Class is created with its required parameters.
3. **Activation** – The automaton enables runtime calls.
4. **State Processing** – State inputs are validated and passed to `_evaluate()`.
5. **Output Generation** – Output is validated and returned.

This design cleanly separates configuration from execution, ensuring maintainability and predictable state handling.

---

## Available Interfaces

Each interface inherits from `HybridComponentInterface`, which provides:
- Initialization and state validation
- Output type checking
- Standard logging
- Metadata access methods

**Interfaces include:**
- **InvariantInterface** – Checks if the automaton can remain in the current mode.
- **GuardInterface** – Determines if a mode transition should occur.
- **ResetInterface** – Updates state variables during a transition.
- **DynamicsInterface** – Defines continuous state evolution.

---

NOTE: For further information please visit the official documentation: ....
