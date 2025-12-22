all:
	cp /usr/lib/x86_64-linux-gnu/libpinyin/data . -rf
	g++ -g main.cpp `pkg-config libpinyin --libs --cflags`
clean:
	rm -rf a.out data
