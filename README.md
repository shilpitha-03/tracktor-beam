
# Setup 
## Tracktor-Beam setup

First clone the repo(inside new) then start by checking if you have already setup OpenCV and check the version using:

    git clone https://github.com/shilpitha-03/tracktor-beam.git -b feature/px4-edited

    pkg-config --modversion opencv4

If its not 4.10.0 then run the following command to get it:

    cd tracktor-beam
    ./install_opencv.sh 
    git submodule update --init --recursive
    colcon build

Build specific packages using
    
    colcon build --packages-select <package>

Source the workspace

    source install/setup.bash 

### Nodes available to run:

#### aruco_tracker

Node to track the aruco marker and return its pose in the camera frame:

    ros2 run aruco_tracker aruco_tracker 

#### marker_trajectory

Node to dynamically update the aruco markers pose along  pre-defined trajectory:

    ros2 run marker_trajectory marker_trajectory

#### wrapper

Node to start the wrapper to wrap the vehicle odometry, depth and aruco markers detected pose according to Elastic-Trackers message type

    ros2 run wrapper wrapper_node
