TARGET=eod_game

all:
	@pyinstaller $(TARGET).spec
	
clean:
	@rm -rf build/ dist/
