# Cricic

A tiny, batteries-excluded CI

![logo](docs/logo.svg)

## Goal

One small python program to handle your CI needs, without being intrusive.
Easy to use, and with as little as possible dependencies, as usual.
Cricic works with `git` for pushing code and `make` for the intermediate steps.

## Status

Many features missing, under heavy development

## Installation

Recommended way: via `make`

```bash
$ git clone https://github.com/jwmng/cricic
$ make install
```

By default, this will copy the config directory to `~/.config/cricic`.
You can change this by overriding the `CONF_ROOT` variable, however, the program
will only search in a few locations (see [Configuration](#Configuration)) or a
custom location specified using the `-c` option.

## Usage

### Quick instructions

1. Initialise a receiving repository on your server:

```
user@server:/repo $ cricic myproject init

Initialised an empty repo in /repo/myproject
To add the remote locally:
    git remote add cricic user@serv:~/myproject

To push to the repository:
    git push cricic dev

```

2. Add the remote locally:

```
user@work:~/myproject $ git remote add serv user@serv:/repo/myproject
```

3. Push some code:

```
user@work:~/myproject $ git push serv dev
```

4. Watch magic happen:

  - `make preprocess` is run and the push is rejected if this fails
  - The files are received, and `make test`, `make build` and `make deploy` are
    run (in that order)

And of course, all of this is [configurable](#Configuration)

### Other commands

- `cricic log` shows the result of the last few CI operations and the current
  commit the server is on.
- `cricic remove` removes all data related to cricic from the repository

Both commands should be run in a cricic reposistory, or supply a directory as
their first argument.

### Specifics

When using `init`, a bare repository is initialised, with two git hooks 
(`post-receive` and `pre-receive`) set to run the cricic scripts.  
These scripts run the `make` targets configured in `config.ini`.

The `post-receive` hook runs in the working directory, by default 
`$repo/cricic/files`.

The default make targets are:

- `preprocess` at the pre-receive hook.
- `test`, `build` and `deploy` at the post-receive hook

Before `post-receive` runs anything, it checks out the files to the `work_dir`.
Relevant data is logged to `~/myproject/cricic/log`, and information about the
current branch/commit is saved to `~/myproject/cricic/state`.

## Configuration

All configuration files use inifile formatting.
The build file ~~looks like~~ _is_ a Makefile.

Configuration files can be put in three places and will read in order:

1. (global) `/etc/cricic/config.ini`
2. (global) `~/.config/cricic/config.ini`
3. (local) `$repository/cricic/config.ini`

### Global settings

The global configuration files may contain defaults that can be overridden on 
a per-repository basis using the local config file.
The following options are supported for global configuration files:

```ini
[general]
; These settings are used to generate the 'git add' URL, and are set to the
; server's hostname username during installation
remote_name = cricic
hostname = user@serv

; Branch and location of the buildfile.
; Note that buildfile location is relative to the repository root
branch = dev
buildfile = cricic/buildfile

[pre]
; Make target for the `pre-receive` hooks, space-separated
targets = preprocess

; Decides if `make` should echo its commands
silent = False

[post]
targets = test build deploy
silent = True
```

Global config options can be overriden in the local config file.

### Local settings

You can use the local configuration file to override global settings, and to set
the repository-specific working directory.
If you feel brave, you can set this to your server's document root for example:

```ini
[repository]
work_dir = /var/www/myproject
```

The `ork_dir` is the directory where files will be put before the `post-receive`
targets are run.

### Buildfile

The buildfile defines what actually happens when the repository receives a push.
By default, it contains very little, and it should be configured to suit your
needs:

```make
.PHONY: preprocess test build deploy

preprocess:
	echo 'Accepted commit'

test:
	echo 'Tests passed'

build:
	echo 'Done building'

deploy:
	echo 'Done deploying'
```

#### Updating the buildfile

To update the buildfile, just add a `.cricic` file to the repository containing
the buildfile contents.
It will be automatically copied to `/repo/cricic/buildfile` and will not be
present in the deployed file (as to not pollute served directories).

## Applied example

Let's say we want the CI to do the following things:

1. Refuse commits during office hours
2. Test our new code using python's `unittest`
3. If successful, install potential new dependencies
4. Move the code to the `/var/www/app`

Our buildfile contains the following:
```make

.PHONY: preprocess test build deploy

HOUR = $(shell date +%H)

preprocess:
    if [ ${HOUR} -lt 16 ] && [ ${HOUR} -gt 8 ]; then\
        echo 'ERROR: You cannot commit during office hours'; exit 1;\
    fi

test:
    virtualenv env; ./env/bin/python -m unittest discover

build:
    virtualenv env; ./env/bin/pip install -r requirements.txt

deploy:
    rsync -r --delete . /var/www/app
```
