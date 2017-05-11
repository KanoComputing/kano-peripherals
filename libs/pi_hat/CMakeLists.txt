cmake_minimum_required (VERSION 2.6)

project (kano_hat C)

include_directories ("${CMAKE_CURRENT_LIST_DIR}/library/include")
find_library (WIRING_PI_LIB wiringPi)

add_library (
    kano_hat SHARED
    "${CMAKE_CURRENT_LIST_DIR}/library/src/setup.c"
    "${CMAKE_CURRENT_LIST_DIR}/library/src/callbacks.c"
    "${CMAKE_CURRENT_LIST_DIR}/library/src/lock.c"
    "${CMAKE_CURRENT_LIST_DIR}/library/src/power_button.c"
    "${CMAKE_CURRENT_LIST_DIR}/library/src/battery.c"
    "${CMAKE_CURRENT_LIST_DIR}/library/src/detection.c"
    "${CMAKE_CURRENT_LIST_DIR}/library/src/ck2_lite_hat/ck2_lite_hat.c"
    "${CMAKE_CURRENT_LIST_DIR}/library/src/ck2_pro_hat/ck2_pro_hat.c"
    ${COMMON_FILES}
)
target_link_libraries (kano_hat ${WIRING_PI_LIB})

add_executable (example EXCLUDE_FROM_ALL "${CMAKE_CURRENT_LIST_DIR}/examples/c/src/main.c")
target_link_libraries (example kano_hat)
target_link_libraries (example ${WIRING_PI_LIB})

add_executable (battery-status "${CMAKE_CURRENT_LIST_DIR}/batt/battery-status.c")
target_link_libraries (battery-status kano_hat)

