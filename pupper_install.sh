#!/bin/bash
######################################################################################
# ROS2
#
# This stack will consist of ROS2 install
#
# To install
#    ./pupper_install.sh
######################################################################################

set -e
echo "setup.sh started at $(date)"

###### work in progress #######

# check Ubuntu version
source /etc/os-release

if [[ $UBUNTU_CODENAME != 'noble' ]]
then
    echo "Ubuntu 24.04 LTS (Noble Numbat) is required"
    echo "You are using $VERSION"
    exit 1
fi

############################################
# wait until unattended-upgrade has finished
############################################
tmp=$(ps aux | grep unattended-upgrade | grep -v unattended-upgrade-shutdown | grep python | wc -l)
[ $tmp == "0" ] || echo "waiting for unattended-upgrade to finish"
while [ $tmp != "0" ];do
sleep 10;
echo -n "."
tmp=$(ps aux | grep unattended-upgrade | grep -v unattended-upgrade-shutdown | grep python | wc -l)
done

cd ~
sudo apt-get update
sudo apt -y install python3-pip python3-venv python3-virtualenv

#Auto install ROS2 Jazzy
if ! [ -d "ros2_setup_scripts_ubuntu" ]; then
  git clone https://github.com/Tiryoh/ros2_setup_scripts_ubuntu.git
fi
~/ros2_setup_scripts_ubuntu/ros2-jazzy-ros-base-main.sh
source /opt/ros/jazzy/setup.bash

#clone mini pupper ros2 repo
mkdir -p ~/mini_pupper_ws/src
cd ~/mini_pupper_ws/src
if ! [ -d "mini_pupper_ros" ]; then
  git clone https://github.com/MushfiqueTM/mini_pupper_ros_fixed.git -b ros2-jazzy mini_pupper_ros
fi
vcs import < mini_pupper_ros/.minipupper.repos --recursive

# Initialize champ submodule (libchamp headers)
cd ~/mini_pupper_ws/src/champ/champ
git submodule update --init --recursive
cd ~/mini_pupper_ws/src

# Disable broken Gazebo Classic champ packages (not needed on robot)
for pkg in champ_gazebo champ_description champ_bringup champ_navigation champ_config; do
  touch ~/mini_pupper_ws/src/champ/champ/$pkg/COLCON_IGNORE
done
# Disable simulation package (Gazebo not used on robot)
touch mini_pupper_ros/mini_pupper_simulation/AMENT_IGNORE

# install dependencies
cd ~/mini_pupper_ws
rosdep install --from-paths src --ignore-src -r -y \
  --skip-keys="champ_base champ_teleop champ_description champ_gazebo ldlidar_node ldlidar_stl_ros2 gazebo_plugins gazebo_ros gazebo_ros_pkgs gazebo_ros2_control velodyne_gazebo_plugins joint_state_publisher_gui rviz2"

# Install ROS 2 Jazzy packages
sudo apt install -y ros-jazzy-teleop-twist-keyboard
sudo apt install -y ros-jazzy-teleop-twist-joy
sudo apt install -y ros-jazzy-v4l2-camera ros-jazzy-image-transport-plugins
sudo apt install -y ros-jazzy-xacro
sudo apt install -y ros-jazzy-robot-localization
sudo apt install -y ros-jazzy-ros2-controllers
sudo apt install -y ros-jazzy-ros2-control
sudo apt install -y ros-jazzy-navigation2
sudo apt install -y ros-jazzy-nav2-bringup
sudo apt install -y ros-jazzy-slam-toolbox

# New LD Lidar driver dependency
sudo apt install -y libudev-dev

pip3 install simple_pid --break-system-packages

MAKEFLAGS=-j1 colcon build --executor sequential --symlink-install

# Setup udev rules for LD Lidar driver
if [ -d "src/ldlidar" ]; then
    cd ~/mini_pupper_ws/src/ldlidar/scripts/ 2>/dev/null || true
    [ -f create_udev_rules.sh ] && ./create_udev_rules.sh || true
    cd ~/mini_pupper_ws
fi

# show IP address on LCD when boot up
cd ~/mini_pupper_ws/src/mini_pupper_ros/
sudo cp robot.service /etc/systemd/system/
sudo mkdir -p /var/lib/minipupper/
sudo cp run.sh /var/lib/minipupper/
sudo cp show_ip.py /var/lib/minipupper/
sudo chmod +x /var/lib/minipupper/run.sh
sudo systemctl daemon-reload
sudo systemctl enable robot

echo "setup.sh finished at $(date)"
sudo reboot
