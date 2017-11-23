.PHONY: install config clean test

PREFIX = ~/.local
CONF = ~/.config/cricic
TARGET = $(PREFIX)/share/cricic
BIN_DIR = $(PREFIX)/bin

uninstall:
	rm -rf $(TARGET)
	rm -rf $(CONF)
	rm -f $(BIN_DIR)/cricic

config:
	rm -rf $(CONF)
	mkdir $(CONF)
	cp ./conf/* $(CONF)

clean:
	rm -rf cricic/__pycache__

install: uninstall config
	mkdir $(TARGET)
	cp -r * $(TARGET)
	ln -s $(TARGET)/cricic.sh $(BIN_DIR)/cricic

test:
	rm -rf test/repo1
	python -m cricic test/repo1 init
