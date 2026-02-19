from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'stanford_controller'

setup(
    name=package_name,
    version='2.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='MangDang',
    maintainer_email='fae@mangdang.net',
    description='Stanford quadruped controller for Mini Pupper on ROS 2 Jazzy',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'stanford_controller_node = stanford_controller.stanford_controller_node:main',
            'twist_to_command_node = stanford_controller.twist_to_command_node:main',
        ],
    },
)
