cmake_minimum_required(VERSION 3.16)
project(mini_pupper_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config rviz urdf meshes
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  src/stanford_state_publisher.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME stanford_state_publisher
)

install(PROGRAMS
  src/stanford_joint_trajectory_to_states.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME stanford_joint_trajectory_to_states
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
