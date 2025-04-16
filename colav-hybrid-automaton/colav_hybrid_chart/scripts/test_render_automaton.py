import numpy as np

class HybridAutomaton:
    def __init__(self):
        self.mode = "Cruise"
        self.state = np.array([0, 0])  # e.g., position
        self.time = 0

    def update(self, input_data):
        # Evaluate guards
        if input_data["obstacle_near"] and self.mode == "Cruise":
            self.mode = "Avoid"
        # Update continuous state
        self.state += np.array([1, 0])  # placeholder dynamics
        self.time += 1

def refresh_gui():
    current_mode_label.setText(f"Mode: {automaton.mode}")
    plot_canvas.update(automaton.state)
