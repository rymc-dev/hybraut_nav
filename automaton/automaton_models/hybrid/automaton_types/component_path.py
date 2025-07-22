from dataclasses import dataclass
from typing import Any
from utils import import_class

@dataclass
class ComponentPath:
    _module: str
    _class_name: str

    def get_component_class(self) -> Any:
        cls = import_class(self._module, self._class_name)
        return cls

    @classmethod
    def load_component_from_famd(cls, component_dict: dict):
        return cls(
            _module=component_dict['module'],
            _class_name=component_dict['class_name']
        )