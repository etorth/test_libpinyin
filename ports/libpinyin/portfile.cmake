vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO etorth/libpinyin
    REF edf42ea61dc099eee1bb6716112b2998203bcec0
    SHA512 44fa8712a39cc9530ba8a0209a2992abf69e8d2ed7d9dc4936b22a738d8a6dc42c3753387777557462bffdc4721ce6d5e880fd9513e34b3c1c0c9e325cfa1553
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

vcpkg_configure_make(
    SOURCE_PATH "${SOURCE_PATH}"
    AUTOCONFIG
    OPTIONS
        --with-dbm=BerkeleyDB
        --disable-libzhuyin
        --disable-dependency-tracking
)

vcpkg_install_make()

vcpkg_fixup_pkgconfig()

file(REMOVE_RECURSE
    "${CURRENT_PACKAGES_DIR}/debug/include"
    "${CURRENT_PACKAGES_DIR}/debug/share"
    "${CURRENT_PACKAGES_DIR}/share/doc"
)

vcpkg_install_copyright(FILE_LIST "${SOURCE_PATH}/COPYING")
