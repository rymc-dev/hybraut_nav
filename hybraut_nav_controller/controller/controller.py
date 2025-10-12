class Controller:
    def __init__(self):
        """
        Base Controller class.
        Override and extend in subclasses.
        """
        pass

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

    def __repr__(self):
        return f"{self.__class__.__name__}()"
