all:
	g++-11 -g main.cpp `pkg-config libpinyin --libs --cflags` -ldb
