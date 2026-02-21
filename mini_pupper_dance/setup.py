from glob import glob
import os

from setuptools import setup

package_name = 'mini_pupper_dance'

setup(
    name=package_name,
    version='1.0.0',
    packages=['mini_pupper_dance', 'mini_pupper_dance.new_dance'],
    package_dir={
        'mini_pupper_dance': 'mini_pupper_dance',
    },
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('launch/*.launch.py')),
    ],
    install_requires=[],
    zip_safe=True,
    maintainer='MangDang',
    maintainer_email='fae@mangdang.net',
    description='Dance choreography package for Mini Pupper on ROS 2 Jazzy',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'service = mini_pupper_dance.dance_server:main',
            'client = mini_pupper_dance.dance_client:main',
            'pose_controller = mini_pupper_dance.pose_controller:main',
            'mini_pupper_dance = mini_pupper_dance.new_dance.mini_pupper_dance:main',
        ],
    },
)
