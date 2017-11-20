"""
Cricic CLI functions
"""

import sys
import subprocess as sp
from configparser import ConfigParser
from pathlib import Path

SHELL = '#!/bin/sh\n'


class RunError(RuntimeError):
    """ Custom error for message passing to CLI """
    def __init__(self, msg):
        super(RunError, self).__init__()
        self.msg = msg


def init(repository, **_):
    """ Initialise repository, add config, link hooks to cricic """

    cricic_root = Path('.').resolve()
    conf_root = cricic_root / 'conf'

    # Quick checks
    repository = Path(repository)
    if repository.is_dir() and list(repository.glob('*')):
        raise RunError("Directory exists and is not empty")

    # Parent directory must exist
    if not list(repository.parents)[0].is_dir():
        raise RunError("Cannot create directory")

    # Initialise
    sp.run(('git', 'init', '-q', '--bare', repository))
    print("-- Initialising Cricic receiving repository")
    print("Initialised an empty repository in %s" % str(repository))

    # Add hooks
    for hook in ('pre-receive', 'post-receive'):
        hook_script = (cricic_root / 'cricic.sh')
        hook_cmd = SHELL + 'cd %s\n' % str(cricic_root)
        hook_cmd = hook_cmd + (' '.join([str(hook_script),
                                         str(repository.resolve()),
                                         '@'+hook]))

        with open((repository / 'hooks' / hook), 'a+') as hook_file:
            hook_file.write(hook_cmd)

    print("Wrote deploy hooks")

    # Create dir
    repo_conf_dir = repository / 'cricic'
    repo_conf_dir.mkdir()

    # Add default build file as binary
    buildfile_content = (conf_root / 'buildfile.sample').read_bytes()
    buildfile_path = repo_conf_dir / 'buildfile'
    buildfile_path.write_bytes(buildfile_content)
    print("Added sample buildfile (%s)" % buildfile_path)

    # Add empty config file
    local_conf_path = repo_conf_dir / 'config.ini'
    local_conf_path.touch()
    print("Added empty config file (%s)" % local_conf_path)
    print("-- Done\n")

    # Show info
    confp = ConfigParser()
    confp.read(conf_root / 'config.ini')
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
    print(kwargs)
