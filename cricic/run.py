"""
Cricic CLI functions
"""

import sys
import subprocess as sp
from configparser import ConfigParser
from pathlib import Path

SHELL = '#!/bin/sh\n'
HOOKS = ('pre-receive', 'post-receive')
CRICIC_ROOT = Path('.').resolve()
CONF_ROOT = CRICIC_ROOT / 'conf'
HOOK_SCRIPT = (CRICIC_ROOT / 'cricic.sh')


class RunError(RuntimeError):
    """ Custom error for message passing to CLI """
    def __init__(self, msg):
        super(RunError, self).__init__()
        self.msg = msg


def init(repository, **_):
    """ Initialise repository, add config, link hooks to cricic """

    # Quick checks
    repository = Path(repository)
    if repository.is_dir() and list(repository.glob('*')):
        raise RunError("Directory exists and is not empty")

    # Parent directory must exist
    if not list(repository.parents)[0].is_dir():
        raise RunError("Cannot create directory")

    # Initialise
    sp.run(('git', 'init', '-q', '--bare', repository))

    # Add hooks
    for hook in HOOKS:
        hook_cmd = SHELL + 'cd %s\n' % str(CRICIC_ROOT)
        hook_cmd = hook_cmd + (' '.join([str(HOOK_SCRIPT),
                                         str(repository.resolve()),
                                         '@'+hook]))

        with open((repository / 'hooks' / hook), 'a+') as hook_file:
            hook_file.write(hook_cmd)

    # Create dir
    repo_conf_dir = repository / 'cricic'
    repo_conf_dir.mkdir()

    # Add default build file as binary
    buildfile_content = (CONF_ROOT / 'buildfile.sample').read_bytes()
    buildfile_path = repo_conf_dir / 'buildfile'
    buildfile_path.write_bytes(buildfile_content)

    # Add empty config file
    local_conf_path = repo_conf_dir / 'config.ini'
    local_conf_path.touch()
    print("Initialised an empty cricic repository in %s" % str(repository))

    # Show info
    confp = ConfigParser()
    confp.read(CONF_ROOT / 'config.ini')
    print("To add repository:\n"
          "\tgit remote add %s %s:%s" % (confp.get('general', 'remote_name'),
                                         confp.get('general', 'hostname'),
                                         repository.resolve()))
    print("")
    print("To push changes:\n"
          "\tgit push %s %s" % (confp.get('general', 'remote_name'),
                                confp.get('general', 'branch')))


def info(repository, **kwargs):
    print(repository)
    print(kwargs)


def remove(repository, **kwargs):
    remove_confirm = input("Remove repository along with cricic files? [y/n] ")
    remove_repo = remove_confirm.lower() in ('y', 'yes')

    [(repository / hook).unlink() for hook in HOOKS]
    [f.unlink() for f in CONF_ROOT.glob('*')]
    CONF_ROOT.rmdir()
