vcpkg_download_distfile(ARCHIVE
    URLS "https://dbmx.net/kyotocabinet/pkg/kyotocabinet-${VERSION}.tar.gz"
    FILENAME "kyotocabinet-${VERSION}.tar.gz"
    SHA512 9fe0a92c9a76db5ce06ef4d5a551c05930f2a9c065ab695b030fdaf45692bfe88d91f1b75791f50d0772c699567744cd74f3ef407172874d4bba467989d54328
)

vcpkg_extract_source_archive(SOURCE_PATH
    ARCHIVE "${ARCHIVE}"
    SOURCE_BASE "${VERSION}"
    PATCHES
        mingw-ucrt64-fixes.patch
)

vcpkg_configure_make(
    SOURCE_PATH "${SOURCE_PATH}"
    COPY_SOURCE
    OPTIONS
        --disable-zlib
        --disable-lzo
        --disable-lzma
)

vcpkg_install_make()
vcpkg_fixup_pkgconfig()

file(REMOVE_RECURSE
    "${CURRENT_PACKAGES_DIR}/debug/bin"
    "${CURRENT_PACKAGES_DIR}/debug/include"
    "${CURRENT_PACKAGES_DIR}/debug/share"
    "${CURRENT_PACKAGES_DIR}/share/doc"
    "${CURRENT_PACKAGES_DIR}/share/man"
)

vcpkg_install_copyright(
    FILE_LIST
        "${SOURCE_PATH}/COPYING"
        "${SOURCE_PATH}/FOSSEXCEPTION"
)
