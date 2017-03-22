cmake_minimum_required (VERSION 2.6)

project (kano_hat C)

include_directories ("${PROJECT_SOURCE_DIR}/library/includes")

find_library (WIRING_PI_LIB wiringPi)

add_library (
    kano_hat SHARED
    "${PROJECT_SOURCE_DIR}/library/src/kano_hat.c"
    "${PROJECT_SOURCE_DIR}/library/src/callbacks.c"
    "${PROJECT_SOURCE_DIR}/library/src/lock.c"
    "${PROJECT_SOURCE_DIR}/library/src/power_button.c"
    "${PROJECT_SOURCE_DIR}/library/src/detection.c"
)
target_link_libraries (kano_hat ${WIRING_PI_LIB})

add_executable (example EXCLUDE_FROM_ALL "${PROJECT_SOURCE_DIR}/examples/c/src/main.c")
target_link_libraries (example kano_hat)
target_link_libraries (example ${WIRING_PI_LIB})

add_definitions (-DUSERSPACE)
