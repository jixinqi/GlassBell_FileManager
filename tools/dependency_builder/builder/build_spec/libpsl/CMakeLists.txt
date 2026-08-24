cmake_minimum_required(VERSION 3.15)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_EXPORT_COMPILE_COMMANDS 1)

project(psl)

set(${PROJECT_NAME}_INC     "")
set(${PROJECT_NAME}_INC_DIR "")
set(${PROJECT_NAME}_SRC     "")
set(${PROJECT_NAME}_SRC_DIR "")
set(${PROJECT_NAME}_LIB     "")
set(${PROJECT_NAME}_LIB_DIR "")

set(PROGRAM_NAME
    "${PROJECT_NAME}"
)
add_library(psl
    "${CMAKE_SOURCE_DIR}/src/psl.c"
    "${CMAKE_SOURCE_DIR}/src/lookup_string_in_fixed_set.c"
)
target_include_directories(${PROJECT_NAME} PUBLIC
    "${CMAKE_SOURCE_DIR}/"
    "${CMAKE_SOURCE_DIR}/include/"
)
target_compile_definitions(${PROJECT_NAME} PRIVATE
    "ENABLE_BUILTIN"
    "BUILDING_PSL"
    PACKAGE_VERSION="0.21.5"
)
if(NOT BUILD_SHARED_LIBS)
    target_compile_definitions(${PROJECT_NAME} PUBLIC "PSL_STATIC")
endif()
install(DIRECTORY "${CMAKE_SOURCE_DIR}/include/"
    DESTINATION "include"
    FILES_MATCHING PATTERN "*.h"
)
install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION "lib"
    LIBRARY DESTINATION "lib"
    RUNTIME DESTINATION "bin"
)
