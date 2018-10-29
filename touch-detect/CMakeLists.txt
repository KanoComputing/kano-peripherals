cmake_minimum_required(VERSION 2.8)
project(TouchDetect CXX)

if(EXISTS ${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    conan_basic_setup()
endif()


if (APPLE)  # OS X
    set(LINK_LIBS "")
    set(PLATFORM_SRC lib/platforms/macosx)
elseif (UNIX AND NOT APPLE)  # Linux
    set(LINK_LIBS X11 Xi)
    set(PLATFORM_SRC lib/platforms/linux)
endif()


set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)


add_library(touch_detect_lib SHARED
    ${PLATFORM_SRC}/touch_detect.cpp
)
target_link_libraries(touch_detect_lib ${LINK_LIBS})
set_target_properties(touch_detect_lib PROPERTIES OUTPUT_NAME "touch_detect")
target_include_directories(touch_detect_lib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)


add_library(touch_detect_lib_static STATIC
    ${PLATFORM_SRC}/touch_detect.cpp
)
target_link_libraries(touch_detect_lib_static ${LINK_LIBS})
set_target_properties(touch_detect_lib_static PROPERTIES OUTPUT_NAME "touch_detect")
target_include_directories(touch_detect_lib_static PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)


add_executable(touch_detect
    src/main.cpp
)
set_target_properties(touch_detect PROPERTIES OUTPUT_NAME "touch-detect")
target_link_libraries(touch_detect
    touch_detect_lib
)
