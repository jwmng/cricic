.PHONY: install config clean test

CONF_PREFIX = ~/.config
CONF = $(CONF_PREFIX)/cricic
ENV_NAME = env

env:
	virtualenv $(ENV_NAME)
	echo 'Run `source $(ENV_NAME)` to activate env'

uninstall:
	rm -rf $(CONF)

config:
	echo "Building config file"
	cat conf/config.ini.sample | sed \
		-e 's/&user/$(shell whoami)/' \
		-e 's/&serv/$(shell hostname)/' > conf/config.ini

clean:
	python setup.py clean
	rm -f conf/config.ini
	rm -rf Cricic.egg-info
	rm -rf $(CONF)

install: config
	python setup.py install

test:
	rm -rf test/repo1
	python -m cricic test/repo1 init
