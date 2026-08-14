class Controller:
    def __init__(self):
        """
        Base Controller class.
        Override and extend in subclasses.
        """
        pass

    def update_continous_dynamics(self, *args, **kwargs):
        raise NotImplementedError("update_continous_dynamics() must be implemented in subclass.")

    def update_state(self, *args, **kwargs):
        """
        Update the controller's internal state.
        Should be implemented by subclasses.
        """
        raise NotImplementedError("update_state() must be implemented in subclass.")

    def step(self):
        """
        Compute and return the control command.
        Should be implemented by subclasses.
        """
        raise NotImplementedError("step() must be implemented in subclass.")

    def reset(self):
        """
        Clear any state accumulated across step() calls (e.g. integral/
        derivative history) so a controller that's been idle doesn't carry
        stale history into its next active period. No-op by default -
        override in subclasses that actually hold such state.
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}()"
