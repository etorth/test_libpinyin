g++-11 main.cpp `env PKG_CONFIG_PATH=/home/anhong/b_mir2x_debug/3rdparty/libpinyin/build/install/lib/pkgconfig pkg-config libpinyin --libs --cflags` -ldb
env LD_LIBRARY_PATH=/home/anhong/b_mir2x_debug/3rdparty/libpinyin/build/install/lib ./a.out
