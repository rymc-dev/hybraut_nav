from dataclasses import dataclass
from typing import Type
from hybraut_utils import import_class

@dataclass
class MsgType:
    """Helper class for message type specification."""
    pkg: str
    msg: str

    def import_msg_type(self) -> Type:
        return import_class(
            module_path=self.pkg,
            class_name=self.msg
        )