vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO libpinyin/libpinyin
    REF "${VERSION}"
    SHA512 ef9316fc4e429821fa9d9f1edba0c4f9918ac1f69d6cabfbfb60acd330db3078e7b38f3f61ddbdbaafbd7d1eb1d082c0257b871dfe6d81de3c4c72adefe6e431
    HEAD_REF main
)

vcpkg_download_distfile(MODEL_ARCHIVE
    URLS "https://downloads.sourceforge.net/project/libpinyin/models/model20.text.tar.gz"
    FILENAME "libpinyin-model20.text.tar.gz"
    SHA512 ed4d0607ad35e0e7ea424670539ddcd81a2b03c1da914b9c00cb748cf065f29471502d40b9a189852001da1fb9178c3bcc4675d7efebea5d081d78bfeee9b5d6
)

vcpkg_extract_source_archive(MODEL_SOURCE_PATH
    ARCHIVE "${MODEL_ARCHIVE}"
    SOURCE_BASE "model20"
    NO_REMOVE_ONE_LEVEL
)
file(COPY "${MODEL_SOURCE_PATH}/" DESTINATION "${SOURCE_PATH}/data")

set(KYOTOCABINET_PRIVATE_LIBS)
if(VCPKG_TARGET_IS_LINUX)
    list(APPEND KYOTOCABINET_PRIVATE_LIBS -lstdc++ -lrt -lpthread -lm -lc)
elseif(VCPKG_TARGET_IS_OSX)
    list(APPEND KYOTOCABINET_PRIVATE_LIBS -lc++ -lpthread -lm)
endif()
string(JOIN " " KYOTOCABINET_CONFIGURE_LIBS ${KYOTOCABINET_PRIVATE_LIBS})

vcpkg_configure_make(
    SOURCE_PATH "${SOURCE_PATH}"
    AUTOCONFIG
    OPTIONS
        --with-dbm=KyotoCabinet
        --disable-libzhuyin
        --disable-dependency-tracking
        "LIBS=${KYOTOCABINET_CONFIGURE_LIBS}"
)

vcpkg_install_make()

foreach(pc_file IN ITEMS
    "${CURRENT_PACKAGES_DIR}/lib/pkgconfig/libpinyin.pc"
    "${CURRENT_PACKAGES_DIR}/debug/lib/pkgconfig/libpinyin.pc"
)
    if(EXISTS "${pc_file}")
        vcpkg_replace_string("${pc_file}" "Requires: glib-2.0" "Requires: glib-2.0\nRequires.private: kyotocabinet")
    endif()
endforeach()

vcpkg_fixup_pkgconfig()

file(REMOVE_RECURSE
    "${CURRENT_PACKAGES_DIR}/debug/include"
    "${CURRENT_PACKAGES_DIR}/debug/share"
    "${CURRENT_PACKAGES_DIR}/share/doc"
)

vcpkg_install_copyright(FILE_LIST "${SOURCE_PATH}/COPYING")
