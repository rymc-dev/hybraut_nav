# test_component_and_msg.py
import pytest
from hybraut_models.ldr import ComponentPath, MsgType
from hybraut_utils import import_class


# --- Tests for ComponentPath ---

def test_component_path_get_component_class():
    # Using a built-in module for testing
    component_path = ComponentPath(_module="math", _class_name="sqrt")
    cls = component_path.get_component_class()
    import math
    assert cls is math.sqrt

def test_component_path_load_component_from_famd():
    component_dict = {"module": "math", "class_name": "sqrt"}
    component_path = ComponentPath.load_component_from_famd(component_dict)
    import math
    assert component_path._module == "math"
    assert component_path._class_name == "sqrt"
    assert component_path.get_component_class() is math.sqrt


# --- Tests for import_class and MsgType ---

def test_import_class_success():
    cls = import_class("math", "sqrt")
    import math
    assert cls is math.sqrt

def test_import_class_failure():
    with pytest.raises(ImportError):
        import_class("math", "nonexistent_class")

def test_msg_type_import_msg_type():
    msg_type = MsgType(pkg="math", msg="sqrt")
    cls = msg_type.import_msg_type()
    import math
    assert cls is math.sqrt


if __name__ == '__main__':
    pytest.main([__file__])
