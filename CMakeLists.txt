cmake_minimum_required(VERSION 3.10)
project(driverless)
set(CMAKE_OSX_ARCHITECTURES "arm64")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


# Set the OpenCV_DIR to the OpenCV config path installed by Homebrew
set(OpenCV_DIR /opt/homebrew/Cellar/opencv/4.12.0_11/lib/cmake/opencv4)
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(${CMAKE_SOURCE_DIR}/src)
include_directories(${CMAKE_SOURCE_DIR}/include)

# Main executable
add_executable(driverless main.cpp src/utils.cpp src/detection.cpp src/track.cpp)
target_link_libraries(driverless ${OpenCV_LIBS})
