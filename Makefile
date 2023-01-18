all:
	cp /usr/lib/x86_64-linux-gnu/libpinyin/data . -rf
	g++-11 -g main.cpp `pkg-config libpinyin --libs --cflags` -ldb
clean:
	rm -f a.out
