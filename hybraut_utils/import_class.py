"""
simple utility for dynamic importing of classes utilizing
module_path and class_name
"""

from typing import Type, Any
import importlib


def import_class(module_path: str, class_name: str) -> Type[Any]:
    """
    Dynamically import and return a class from a module.
    """
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Cannot import '{class_name}' from '{module_path}': {e}")
