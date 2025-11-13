import os
import sys

sys.path.append(os.path.dirname(__file__))

from hybrid_automaton_sim import HybridAutomaton, HybridState, HybridTransition, IntegrationMethod
import numpy as np


# =============================================================================
# Example 1: Thermostat (Simple scalar continuous state)
# =============================================================================
class Thermostat(HybridAutomaton):
    """Simple thermostat with heating and cooling modes"""
    
    heating = HybridState(
        "Heating", 
        initial=True, 
        flow=lambda T: 0.1 * (25 - T),
        invariant=lambda T: T <= 23  # Optional: enforce upper bound
    )
    
    cooling = HybridState(
        "Cooling", 
        flow=lambda T: -0.07 * (T - 15),
        invariant=lambda T: T >= 17  # Optional: enforce lower bound
    )
    
    cool = heating.to(cooling)
    heat = cooling.to(heating)
    
    def __init__(self, T0: float = 20.0):
        self.T = T0
        super().__init__()
        
        # Define transitions with guards and optional resets
        self.transitions_map = {
            "cool": HybridTransition(
                guard=lambda T: T >= 22,
                reset=lambda T: T * 0.95,  # Instant 5% drop when switching to cooling
                priority=1
            ),
            "heat": HybridTransition(
                guard=lambda T: T <= 18,
                reset=None,  # No reset
                priority=1
            )
        }
    
    @property
    def continuous_state(self):
        return self.T
    
    @continuous_state.setter
    def continuous_state(self, value):
        self.T = value

import matplotlib.pyplot as plt

def demo_thermostat():
    """Demonstrate thermostat example"""
    print("=" * 70)
    print("Example 1: Thermostat")
    print("=" * 70)
    
    thermo = Thermostat(T0=20.0)
    thermo.enable_event_detection(True, tolerance=1e-4)
    
    results = thermo.simulate(duration=200, dt=0.1, record_states=True)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Temperature plot
    ax1.plot(results['time'], results['continuous'], label='Temperature', linewidth=2)
    ax1.axhline(22, color='r', linestyle='--', alpha=0.5, label='Upper threshold')
    ax1.axhline(18, color='b', linestyle='--', alpha=0.5, label='Lower threshold')
    ax1.set_ylabel('Temperature (°C)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Thermostat: Temperature Control')
    
    # State plot
    states_numeric = [1 if s == 'heating' else 0 for s in results['discrete']]
    ax2.fill_between(results['time'], states_numeric, alpha=0.3, step='post')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('State')
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(['cooling', 'heating'])
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('thermostat.png', dpi=150, bbox_inches='tight')
    print("Saved: thermostat.png")

if __name__ == '__main__':
    demo_thermostat()