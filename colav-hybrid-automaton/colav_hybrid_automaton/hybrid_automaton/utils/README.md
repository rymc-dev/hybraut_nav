# hybrid_automaton utils

This package contains utility modules for the **ROS 2 Hybrid Automaton Framework**.

Framework-specific utilities are located in the [`framework`](./framework/) directory and are imported via the [`__init__.py`](./__init__.py) file for easy access.

You may add your own custom utility modules to this package, which can be used by **guards**, **resets**, and **dynamics** components.

> **Note:** Please do **not** modify the framework utilities in the `framework` directory. These are essential for core components of the system.
