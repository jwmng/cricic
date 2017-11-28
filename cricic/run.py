"""
Cricic CLI functions
"""

import subprocess as sp
from configparser import ConfigParser
from pathlib import Path

from cricic.constants import CRICIC_ROOT, CONF_ROOT, CONF_LOCATIONS

SHELL = '#!/bin/sh\n'
HOOKS = ('pre-receive', 'post-receive')


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
        hook_cmd = hook_cmd + (' '.join(['python -m cricic',
                                         str(repository.resolve()),
                                         '@'+hook]))

        hookfile_path = repository / 'hooks' / hook
        with open(hookfile_path, 'a+') as hook_file:
            hook_file.write(hook_cmd)

        hookfile_path.chmod(0o744)

    # Create dir
    repo_conf_dir = repository / 'cricic'
    repo_conf_dir.mkdir()

    # Add default build file as binary
    buildfile_content = (CONF_ROOT / 'buildfile.sample').read_bytes()
    buildfile_path = repo_conf_dir / 'buildfile'
    buildfile_path.write_bytes(buildfile_content)

    # Add empty config file
    local_conf_path = repo_conf_dir / 'config.ini'
    local_conf_parser = ConfigParser()
    local_conf_parser.add_section('repository')
    local_conf_parser.set('repository', 'work_dir', './files')
    with open(local_conf_path, 'a+') as local_conf_file:
        local_conf_parser.write(local_conf_file)

    print("Initialised an empty cricic repository in %s" % str(repository))

    # Show info
    confp = ConfigParser()
    for conf_path in CONF_LOCATIONS:
        confp.read(conf_path/'config.ini')

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
    remove_confirm = input("Remove cricic files? [y/n] ")
    remove_repo = remove_confirm.lower() in ('y', 'yes')
    if not remove_repo:
        return

    repo_conf_dir = repository / 'cricic'

    [(repository / 'hooks' / hook).unlink() for hook in HOOKS]
    [f.unlink() for f in repo_conf_dir.glob('*')]
    repo_conf_dir.rmdir()
