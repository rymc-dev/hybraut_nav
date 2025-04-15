# colav_hybrid_eval

This package contains implementations of COLAV's hybrid automaton Guard conditions dynamics and resets, It provides services for requesting the states of each of these different components which make the automaton.

# Table of Contents

- [Installation](#installation)
- [Strucutre](#structure)
- [Usage](#usage)
- [Testing](#testing)

## Installation
TODO

## Structure
TODO

## Usage
TODO

## Testing

Testing for this pkg can be executed locally via running 
```bash
chmod +x run_tests.sh
./run_tests.sh
```

This will run tests written in the tests directory and generate a html coverage report which will be found in [`coverage report`](./htmlcov)
to view the coverage report in browser assuming you are in linux you can run: 
```bash
xdg-open htmlcov/index.html
```

(if this does not work you need to install xdg-utils pre-emptively)
```bash
sudo apt update
sudo apt install xdg-utils
```

otherwise testing this using colcon, in the ros2_ws of the pkg
```bash
colcon build
colcon test
```


## License

`colav_hybrid_eval` is distributed under the terms of the [MIT](./LICENSE) license.