# hybraut_ros2

`hybraut_ros2` is a ROS 2 framework for implementing **formal-method hybrid automata**.  
It supports a **multi-hierarchical architecture**, allowing you to define and customize automaton elements—such as states, modes, transitions, guards, resets, and dynamics—without heavy low-level coding.

This design makes it both **flexible** and **high-performance**, enabling advanced control logic for autonomous systems while preserving maintainability and modularity.

NOTE: `for the full extensive documentation of this project, go to this page: [](https://www.notion.so/Automaton-Framework-2326804d21c580faa721edd1a8d4a914#2326804d21c580b99ac4eb5cdcc1966b)`

# Table of Contents

- [Installation](#installation)
- [Structure](#structure)
- [Usage](#usage)

## Installation

pre-requisites: 
 - Must be within an instance of ubuntu using a version of ROS2 with version greater than humble.
 - pip must be installed and configured

 installation steps: 

```bash
mkdir -p ~/ros2_ws/src && git clone {} && git clone {} && cd hybraut_ros2 && pip install -r requirements.txt && cd ~/ros2_ws && colcon build --packages-select hybraut_interfaces hybraut_ros2 && . install/setup.bash 
```

assuming everything worked as expected this bash script should setup the hybraut_ros2 system in a ros2 environment and make it ready to use.

## Structure

The structure of the `hybraut_ros2` project is as follows: 

```bash
hybraut_ros2
├── example_hybraut_ros2_amdls
├── hybraut_aci
├── hybraut_common_behaviours
├── hybraut_execution_engine
├── hybraut_factory
├── hybraut_lifecycle
├── hybraut_models
├── hybrid-automaton.dockerfile
├── launch
├── LICENSE
├── package.xml
├── README.md
├── requirements.txt
├── resource
├── run_tests.sh
├── setup.cfg
├── setup.py
├── tests
└── utils
```

the objective of this project structure is to segment the different components of hybraut_ros2 into seperate packages
based on their system operational phase. discussed in the architecture of the project.

## Usage

examples implementation and demostration of this package in use can be found !()[]

## License

`colav_hybrid_eval` is distributed under the terms of the [MIT](./LICENSE) license.
