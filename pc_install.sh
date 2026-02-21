#!/bin/bash
######################################################################################
# ROS2
#
# This stack will consist of ROS2 install
#
# To install
#    ./pc_install.sh
######################################################################################

# Update package lists
cd ~
sudo apt update

# Install ROS 2 Jazzy setup scripts
if ! [ -d "ros2_setup_scripts_ubuntu" ]; then
  git clone https://github.com/Tiryoh/ros2_setup_scripts_ubuntu.git
fi
~/ros2_setup_scripts_ubuntu/ros2-jazzy-ros-base-main.sh
source /opt/ros/jazzy/setup.bash

# Create ROS 2 workspace and clone Mini Pupper ROS repository
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
if ! [ -d "mini_pupper_ros" ]; then
  git clone https://github.com/mangdangroboticsclub/mini_pupper_ros.git -b ros2-dev mini_pupper_ros
fi
vcs import < mini_pupper_ros/.minipupper.repos --recursive

# Install dependencies and build the ROS 2 packages
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
# Install ROS 2 Jazzy packages (based on Unitree Go2 working configuration)
sudo apt install -y ros-jazzy-teleop-twist-keyboard ros-jazzy-teleop-twist-joy
sudo apt install -y ros-jazzy-v4l2-camera ros-jazzy-image-transport-plugins
sudo apt install -y ros-jazzy-rqt*

# Gazebo Harmonic packages (from Unitree Go2 reference)
sudo apt install -y ros-jazzy-gz-ros2-control
sudo apt install -y ros-jazzy-xacro
sudo apt install -y ros-jazzy-robot-localization
sudo apt install -y ros-jazzy-ros2-controllers
sudo apt install -y ros-jazzy-ros2-control

# Optional: Velodyne for advanced simulation
sudo apt install -y ros-jazzy-velodyne
sudo apt install -y ros-jazzy-velodyne-description

# New LD Lidar driver dependency (from Myzhar repo)
sudo apt install -y libudev-dev

pip3 install simple_pid --break-system-packages
colcon build --symlink-install
