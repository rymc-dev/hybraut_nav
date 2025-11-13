import os
import sys

sys.path.append(os.path.dirname(__file__))

from hybrid_automaton_sim import HybridAutomaton, HybridState, HybridTransition, IntegrationMethod
import numpy as np

class BouncingBall(HybridAutomaton):
    """Ball bouncing under gravity with energy loss"""
    
    falling = HybridState(
        "Falling",
        initial=True,
        flow=lambda x: np.array([x[1], -9.81]),  # [position, velocity]
        invariant=lambda x: x[0] >= 0  # position >= 0
    )
    
    bounce = falling.to(falling)  # Self-transition
    
    def __init__(self, h0: float = 10.0, v0: float = 0.0, restitution: float = 0.8):
        self.x = np.array([h0, v0])  # [height, velocity]
        self.restitution = restitution
        super().__init__()
        
        self.transitions_map = {
            "bounce": HybridTransition(
                guard=lambda x: x[0] <= 0 and x[1] < 0,  # Hit ground with downward velocity
                reset=lambda x: np.array([0, -self.restitution * x[1]]),  # Reverse velocity with loss
                priority=1
            )
        }
    
    @property
    def continuous_state(self):
        return self.x
    
    @continuous_state.setter
    def continuous_state(self, value):
        self.x = value

import matplotlib.pyplot as plt

def demo_bouncing_ball():
    """Demonstrate bouncing ball example"""
    print("\n" + "=" * 70)
    print("Example 2: Bouncing Ball")
    print("=" * 70)
    
    ball = BouncingBall(h0=10.0, v0=0.0, restitution=0.8)
    ball.enable_event_detection(True, tolerance=1e-5)
    ball.set_integration_method(IntegrationMethod.RK4)
    
    results = ball.simulate(duration=10, dt=0.01, record_states=True)
    
    heights = results['continuous'][:, 0]
    velocities = results['continuous'][:, 1]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    ax1.plot(results['time'], heights, linewidth=2)
    ax1.axhline(0, color='k', linestyle='--', alpha=0.3)
    ax1.set_ylabel('Height (m)')
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Bouncing Ball: Height and Velocity vs Time')
    
    ax2.plot(results['time'], velocities, linewidth=2, color='orange')
    ax2.axhline(0, color='k', linestyle='--', alpha=0.3)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Velocity (m/s)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('bouncing_ball.png', dpi=150, bbox_inches='tight')
    print("Saved: bouncing_ball.png")


if __name__ == "__main__":
    demo_bouncing_ball()