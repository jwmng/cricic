# Cricic

A tiny, batteries-excluded CI

![logo](docs/logo.svg)

## Goal

One small python program to handle your CI needs, without being intrusive.
Easy to use, and with as little as possible dependencies, as usual.
Cricic works with `git` for pushing code and `make` for the intermediate steps.

## Usage

### Quick instructions

Assume a code project called `myproject`, a server called `serv` and a
workstation called `work`.
The receiving repositories on `serv` are in `/repo`
The folder `~/myproject` on `work` contains is the working directory and git
repository.

First, initialise the receiving repository:

    user@serv:~ $ cricic init myproject

    Initialised an empty repo in /repo/myproject
    To add the remote locally:
        git add serv user@serv:~/myproject

    To push to the repository:
        git push serv dev

The following things happen:

1. An empty bare git repository is initialised in the folder `myproject`
2. The git hooks (in `/repo/myproject/hooks`) are linked to the cricic script
3. The default repository config is added in `/repo/myproject/cricic/config`
4. Instructions are displayed for locally adding the remote

All repository-related files live in `/repo/myproject/cricic`, this includes the
settings, logs, etc

Note that the name of the remote is here equal to the hostname of the server, 
and the branch is by default `dev`.
These options are both configurable.

After initalising, add the remote locally:

    user@work:~/myproject $ git remote add serv user@serv:/repo/myproject

And push some code:

    user@work:~/myproject $ git push serv dev

The following happens:

1. The pre-receive hook is run (`preprocess` by default), and the push is
   rejected if this fails
2. The files are received
3. The post-receive is run, this will run the `test`, `build` and `deploy`
   targets and complain if anything fails

### Other commands

- `cricic log`:  shows the result of the last few CI
  operations and the current commit the server is on.
- `cricic remove`: Removes all data related to cricic from the repository

Both commands should be run in a cricic reposistory, or supply a directory as
their first argument.

### Specifics

When using `init`, two git hooks (`post-receive` and `pre-receive`) are
symlinked to the cricic scripts.
These scripts run the `make` targets configured in 
`/repo/myproject/cricic/buildfile`.
The `post-receive` hook runs in the `/repo/myproject/cricic/files` folder which
contains the git working tree.

The make targets are:

- `pre-receive` runs the `preprocess`
- `post-receive` runs (in that order) `make test`, `make build` and `make
  deploy`

Before `post-receive` runs anything, it checks out the files to the `work_dir`,
which it will delete when it is done.
Relevant data is logged to `~/myproject/cricic/log`, and information about the
current branch/commit is saved to `~/myproject/cricic/state`.

## Configuration

All configuration files use inifile formatting.
The build file ~~looks like~~ _is_ a Makefile.

### Settings

The global configuration (`~/.config/cricic`) file contains defaults that can 
be overridden on a per-repository basis using the local config file.
By default, it looks like this:

```ini
[general]
; Where files are stored, it is best to leave this default.
; these paths are relative to the cricic file in the repository
repo_dir = /repo
work_dir = ./files
logfile = ./log
statefile = ./state
buildfile = ./buildfile

; These are used to generate the `git remote add` command
remote_name = cricic
hostname = user@serv

; Pushes to branches other than the branch configured here will be rejected
branch = dev

[test]
targets = preprocess

[build]
targets = test build deploy
```

Config options can be overriden in the local (`/repo/cricic/config`) file.

### Buildfile

The build file defines all build operations.
By default, the file contains almost nothing, and it should be configured to
suit your needs:

```make
.PHONY: preprocess test build deploy

preprocess:
    echo 'Accepted commit'

test:
    echo 'Done building'

build:
    echo 'Done preparing'

deploy:
    echo 'Done deploying'
```

#### Example

The default buildfile is not really useful, and only gives feedback for use in
logs.
Let's say we want the CI to do the following things:

1. Refuse commits during office hours
2. Test our new code using python's `unittest`
3. If successful, install potential new dependencies
4. Move our code to the `/var/www/app` directory

Our buildfile contains the following:
```make

.PHONY: preprocess test build deploy

HOUR = $(shell date +%H)

preprocess:
    if [ ${HOUR} -lt 16 ] && [ ${HOUR} -gt 8 ]; then\
        echo 'ERROR: You cannot commit during office hours'; exit 1;\
    fi

test:
    ./env/bin/python -m unittest discover

build:
    ./env/bin/pip install -r requirements.txt

deploy:
    rsync -r --delete . /var/www/myproject

```
