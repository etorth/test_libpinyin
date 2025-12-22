all:
	cp /usr/lib/x86_64-linux-gnu/libpinyin/data . -rf
	g++ -g    main.cpp `pkg-config libpinyin --libs --cflags` -o test_pinyin
	g++ -g extract.cpp `pkg-config libpinyin --libs --cflags` -o test_extract
clean:
	rm -rf a.out data test_pinyin test_extract
