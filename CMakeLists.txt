cmake_minimum_required(VERSION 3.22)

if(NOT DEFINED CMAKE_TOOLCHAIN_FILE)
  if(DEFINED ENV{VCPKG_ROOT} AND EXISTS "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake")
    set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
        CACHE FILEPATH "vcpkg toolchain file")
  elseif(EXISTS "${CMAKE_CURRENT_LIST_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake")
    set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_LIST_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake"
        CACHE FILEPATH "vcpkg toolchain file")
  endif()
endif()

project(test_libpinyin VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT DEFINED VCPKG_INSTALLED_DIR OR NOT DEFINED VCPKG_TARGET_TRIPLET)
  message(FATAL_ERROR "Configure this project with the vcpkg toolchain, preferably via ./build.py.")
endif()

find_package(PkgConfig REQUIRED)
set(PKG_CONFIG_USE_CMAKE_PREFIX_PATH ON)
set(PKG_CONFIG_ARGN "--static")
pkg_check_modules(GLIB2 REQUIRED IMPORTED_TARGET glib-2.0)
set(PKG_CONFIG_ARGN "")
pkg_check_modules(LIBPINYIN REQUIRED libpinyin)

pkg_get_variable(LIBPINYIN_DATABASE_FORMAT libpinyin database_format)
if(NOT LIBPINYIN_DATABASE_FORMAT STREQUAL "BerkeleyDB")
  message(FATAL_ERROR "vcpkg libpinyin must be configured with --with-dbm=BerkeleyDB; got '${LIBPINYIN_DATABASE_FORMAT}'.")
endif()

pkg_get_variable(LIBPINYIN_PREFIX libpinyin prefix)
set(_vcpkg_prefix "${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}")
get_filename_component(_vcpkg_prefix_real "${_vcpkg_prefix}" REALPATH)
get_filename_component(_libpinyin_prefix_real "${LIBPINYIN_PREFIX}" REALPATH)
string(FIND "${_libpinyin_prefix_real}" "${_vcpkg_prefix_real}" _vcpkg_prefix_pos)
if(NOT _vcpkg_prefix_pos EQUAL 0)
  message(FATAL_ERROR "Refusing system libpinyin from '${LIBPINYIN_PREFIX}'. Expected vcpkg prefix '${_vcpkg_prefix}'.")
endif()

pkg_get_variable(LIBPINYIN_INCLUDE_DIR libpinyin libpinyinincludedir)
if(NOT EXISTS "${LIBPINYIN_INCLUDE_DIR}/pinyin.h")
  message(FATAL_ERROR "Could not find vcpkg libpinyin headers in '${LIBPINYIN_INCLUDE_DIR}'.")
endif()

find_file(LIBPINYIN_STATIC_LIBRARY
  NAMES libpinyin.a
  PATHS "${_vcpkg_prefix}/lib"
  NO_DEFAULT_PATH
  REQUIRED
)

find_file(LIBDB_STATIC_LIBRARY
  NAMES libdb.a
  PATHS "${_vcpkg_prefix}/lib"
  NO_DEFAULT_PATH
  REQUIRED
)

pkg_get_variable(LIBPINYIN_PKGDATADIR libpinyin pkgdatadir)
set(LIBPINYIN_DATA_DIR "${LIBPINYIN_PKGDATADIR}/data")
if(NOT EXISTS "${LIBPINYIN_DATA_DIR}/table.conf")
  message(FATAL_ERROR "Could not find vcpkg libpinyin data in '${LIBPINYIN_DATA_DIR}'.")
endif()

add_library(vcpkg_libpinyin_static INTERFACE)
target_include_directories(vcpkg_libpinyin_static INTERFACE "${LIBPINYIN_INCLUDE_DIR}")
target_link_libraries(vcpkg_libpinyin_static INTERFACE
  "${LIBPINYIN_STATIC_LIBRARY}"
  "${LIBDB_STATIC_LIBRARY}"
  PkgConfig::GLIB2
)

function(add_libpinyin_test name source)
  add_executable("${name}" "${source}")
  target_link_libraries("${name}" PRIVATE vcpkg_libpinyin_static)

  if(MINGW)
    target_link_options("${name}" PRIVATE -static -static-libgcc -static-libstdc++)
  elseif(CMAKE_SYSTEM_NAME MATCHES "Linux")
    target_link_options("${name}" PRIVATE -static-libgcc -static-libstdc++)
  endif()

  add_custom_command(TARGET "${name}" POST_BUILD
    COMMAND "${CMAKE_COMMAND}" -E copy_directory
            "${LIBPINYIN_DATA_DIR}"
            "$<TARGET_FILE_DIR:${name}>/data"
    VERBATIM
  )
endfunction()

add_libpinyin_test(test_pinyin main.cpp)
add_libpinyin_test(test_extract extract.cpp)
add_libpinyin_test(test_prefix prefix.cpp)

install(TARGETS test_pinyin test_extract test_prefix RUNTIME DESTINATION .)
install(DIRECTORY "${LIBPINYIN_DATA_DIR}" DESTINATION .)
