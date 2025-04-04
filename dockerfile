FROM ros:humble-ros-core-jammy

LABEL project='colav_hybrid_automaton'
LABEL maintainer='Ryan McKee <r.mckee@qub.ac.uk>'
LABEL version='0.0.1'
LABEL description='ROS-based container for the colav_hybrid_automaton application, providing a UDP-ROS bridge and managing control flow within the colav_gateway namespace.'

ARG MODE=container
ENV MODE=${MODE}

# Install bootstrap tools
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    git \
    python3-colcon-common-extensions \
    python3-colcon-mixin \
    python3-rosdep \
    python3-vcstool \
    && rm -rf /var/lib/apt/lists/*

# Bootstrap rosdep
RUN rosdep init && \
    rosdep update --rosdistro $ROS_DISTRO

# Setup colcon mixin and metadata
RUN colcon mixin add default \
    https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml && \
    colcon mixin update && \
    colcon metadata add default \
    https://raw.githubusercontent.com/colcon/colcon-metadata-repository/master/index.yaml && \
    colcon metadata update

# Install ROS 2 packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-ros-base=0.10.0-1* \
    ros-humble-ament-cmake \
    pip \
    && rm -rf /var/lib/apt/lists/*

# Install pip dependencies for colav_gateway
RUN pip install colav-bridge==0.0.2
RUN pip install colav-protobuf-utils==0.1.4
RUN pip install pytest-dependency

# Create workspace directory
RUN mkdir -p /home/ros2_ws/src

# Copy the colav_gateway package into the workspace
# Ensure the colav_gateway directory exists in your build context.
COPY colav-hybrid-automaton /home/ros2_ws/src/colav-hybrid-automaton

# Clone additional ROS package (colav-interfaces)
RUN cd /home/ros2_ws/src && \
    git clone https://github.com/Artemis-QUB-COLAV/colav-interfaces.git || { echo "git clone failed"; exit 1; }

# Build ROS packages in the workspace
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    cd /home/ros2_ws && \
    colcon build && \
    source ./install/setup.bash"

# Append sourcing commands to .bashrc so that the environment is ready on container start
RUN /bin/bash -c "echo 'source /opt/ros/humble/setup.bash' >> /root/.bashrc && \
    echo 'source /home/ros2_ws/install/setup.bash' >> /root/.bashrc"

# Ensure the environment is loaded in subsequent commands
RUN /bin/bash -c "source /root/.bashrc"

# Set the entrypoint command
ENTRYPOINT [ "/bin/bash", "-c", "if [ \"$MODE\" = \"container\" ]; then source /opt/ros/humble/setup.bash && source /home/ros2_ws/install/setup.bash && ros2 launch colav_hybrid_bringup colav_hybrid_automaton.launch.py; else while true; do sleep 30; done; fi" ]
