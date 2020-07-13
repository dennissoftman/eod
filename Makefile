TARGET=eod_game

all:
	@pyinstaller $(TARGET).spec

pak:
	@tar -cpf data.tar cfg/ font/ img/
	@cat data.tar | zlib-flate -compress=5 > data.pak
	@rm data.tar
	
clean:
	@rm -rf build/ dist/
