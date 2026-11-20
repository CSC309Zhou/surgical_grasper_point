cmake_minimum_required(VERSION 3.16)
project(surgical_grasper_point)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/GrasperPoint.msg"
  "msg/GrasperPointArray.msg"
  DEPENDENCIES std_msgs)

ament_get_python_install_dir(PYTHON_INSTALL_DIR)
install(DIRECTORY grasper_point_runtime DESTINATION "${PYTHON_INSTALL_DIR}"
  PATTERN "__pycache__" EXCLUDE)
configure_file(cmake/point_node.in point_node @ONLY)
install(PROGRAMS "${CMAKE_CURRENT_BINARY_DIR}/point_node" DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY launch weights DESTINATION share/${PROJECT_NAME})
install(FILES README.md DESTINATION share/${PROJECT_NAME})

ament_export_dependencies(rosidl_default_runtime)
ament_package()
