from typing import List, Dict, Any
from .core_interfaces import GuardInterface
from .states import States
from dataclasses import dataclass



@dataclass
class GuardWrapper:
    _guard: GuardInterface

    def evaluate_guard(self, states: States):
        pass

    @classmethod
    def load_guard_from_famd(cls, data: Dict[str, Any]) -> 'GuardWrapper':
        pass


class Guards: 
    _guards = List[GuardWrapper]

    def evaluate_guards(self, states: States):
        for guard in self._guards:
            pass

    @classmethod
    def load_guards_from_famd(cls, data: Dict[str, Any]) -> 'Guards':
        pass

