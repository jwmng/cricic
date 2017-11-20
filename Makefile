.PHONY: install config clean test

PREFIX = ~/.local
CONF = ~/.config/cricic
TARGET = $(PREFIX)/share/cricic
BIN_DIR = $(PREFIX)/bin

clean:
	rm -rf $(TARGET)
	rm -f $(BIN_DIR)/cricic

config:
	rm -rf $(CONF)
	mkdir $(CONF)
	cp ./conf/* $(CONF)

install: clean config
	mkdir $(TARGET)
	cp cricic/* $(TARGET)
	ln -s $(TARGET)/__main__.py $(BIN_DIR)/cricic

test:
	rm -rf test/repo1
	python -m cricic test/repo1 init
