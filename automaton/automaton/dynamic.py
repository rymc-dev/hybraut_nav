

@dataclass
class DynamicsWrapper:
    _inst: DynamicsABC

    def evaluate_dynamics():
        pass
    
    def get_dynamic_info():
        pass
    
    def __repr__(self):
        pass
    
    def __str__(self):
        pass

    @classmethod
    def from_famd(cls, data: Dict[str, Any]) -> "DynamicsWrapper":
        dyn_cls = import_class(data['module'], data['class_name'])
        inst: DynamicsABC = dyn_cls(**data.get('configuration', {}))

        return cls(
            _inst=inst,
        )
