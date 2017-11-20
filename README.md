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
set to run the cricic scripts.
These scripts run the `make` targets configured in 
`/repo/myproject/cricic/buildfile`.
The `post-receive` hook runs in the `/repo/myproject/cricic/files` folder which
contains the git working tree.

The make targets are:

- `pre-receive` runs the `preprocess`
- `post-receive` runs (in that order) `make test`, `make build` and `make
  deploy`

Before `post-receive` runs anything, it checks out the files to the `work_dir`.
Relevant data is logged to `~/myproject/cricic/log`, and information about the
current branch/commit is saved to `~/myproject/cricic/state`.

## Configuration

All configuration files use inifile formatting.
The build file ~~looks like~~ _is_ a Makefile.

### Global settings

The global configuration (`~/.config/cricic/config.ini`) file contains defaults 
that can be overridden on a per-repository basis using the local config file.
By default, it looks like this:

```ini
[general]
; These settings are used to generate the 'git add' URL
remote_name = cricic
hostname = user@serv

; Branch and location of the buildfile.
; Note that buildfile location is relative to the repository root
branch = dev
buildfile = cricic/buildfile

[pre]
; Make targets
targets = preprocess
; Decides if `make` should echo its commands
silent = False

[post]
targets = test build deploy
silent = True
```

Config options can be overriden in the local (`/repo/cricic/config.ini`) file.

### Local settings

The local config file (`/repo/cricic/config.ini`) can override all config
options shown above, and has an additional `repository` section:

```ini
[repository]
deploy_dir = /var/www/myproject
```

The `deploy_dir` is the directory where files will be put before the
`post-receive` hook runs.

### Buildfile

The build file defines all build operations.
To update the buildfile, just add a `.cricic` file to the repository containing
the buildfile contents.
It will be automatically copied to `/repo/cricic/buildfile` and will not be
present in the deployed file (as to not pollute served directories).
By default, the file contains almost nothing, and it should be configured to
suit your needs:

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
    rsync -r --delete . /var/www/app
```
