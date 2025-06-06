# Hybrid AutomatonGuards
 This pkg is inw of the core compinebts of the Hybrid Automaton framework
within the ['guards.py'](./guards) we define guard conditional finctions 

each of these functions must follow two basic rules with the code blocks within 
implementations being to the designer.

```python
from your_state_interfaces_pkg.msg import State1, State2

def sample_guard(state_1: State1, state_2: State2) -> bool:
    """
    within here add your custom block code.
    """
    return true
```

then you can add guard to hyvrid_automaton_config for dynamic import.
