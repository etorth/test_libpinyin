all:
	g++-11 -g main.cpp `pkg-config libpinyin --libs --cflags` -ldb
clean:
	rm -f a.out
