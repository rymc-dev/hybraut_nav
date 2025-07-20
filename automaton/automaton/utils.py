import logging
from typing import Type, Any
import importlib

# Configure logging
logger = logging.getLogger(__name__)

def import_class(module_path: str, class_name: str) -> Type[Any]:
    """
    Dynamically import and return a class from a module.
    
    This function enables runtime importing of ROS2 message types based on
    string identifiers, allowing for flexible message type specification.
    
    Args:
        module_path (str): The full module path (e.g., "geometry_msgs.msg")
        class_name (str): The class name to import (e.g., "Twist")
    
    Returns:
        Type[Any]: The imported class type
        
    Raises:
        ImportError: If the module or class cannot be imported
        
    Example:
        >>> msg_type = import_class("geometry_msgs.msg", "Twist")
        >>> twist_msg = msg_type()
    """
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        error_msg = f"Cannot import '{class_name}' from '{module_path}': {e}"
        logger.error(error_msg)
        raise ImportError(error_msg)