from .guard import Guard

class UnsafeConditionsGuard(Guard):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, *state_inputs):
        return super().__call__(*state_inputs)
    
    def _validate_initialization(self, *args, **kwargs):
        return super()._validate_initialization(*args, **kwargs)
    
    def _validate_state_inputs(self, *state_inputs):
        return super()._validate_state_inputs(*state_inputs)