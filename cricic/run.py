"""
Cricic CLI functions
"""

import logging
import subprocess as sp
from configparser import ConfigParser
from pathlib import Path

from cricic.constants import CRICIC_ROOT, CONF_ROOT, CONF_LOCATIONS

SHELL = '#!/bin/sh\n'
HOOKS = ('pre-receive', 'post-receive')
LOG_SUFFIX = 'cricic/cricic.log'


def _is_git_repo(dir_):
    # First check if it i
    try:
        sp.check_call(('git', 'rev-parse', '--git-dir'), cwd=dir_,
                      stderr=sp.PIPE, stdout=sp.PIPE)
        return True
    except sp.CalledProcessError:
        return False


def _log(repository, status, msg):
    log_file = (repository / LOG_SUFFIX).resolve()
    logging.basicConfig(level=logging.INFO, file=str(log_file))
    logging.log("[%s] %s", status, msg)


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

    _log(repository, 'OK', 'Initialised repository')


def info(repository, **_):
    """ Show some information about the repository """

    # Quick check
    if not _is_git_repo(repository.resolve()):
        print("ERR: %s is not a git repository" % repository)
        return

    print("# Repository: %s" % repository.resolve().stem)

    # Git info
    try:
        commit_hash, message, ago = sp.check_output((
            'git', 'log', '--all',
            '--pretty=format:%h|%s|%cr',
            '-n', '1'
            )).decode('utf-8').split('|')
        print("## Current commit")
        print("SHA1    : %s" % commit_hash)
        print("Message : %s" % message)
        print("Time    : %s" % ago)

    except sp.CalledProcessError:
        print("\n## Could not load current commit")

    # Get log lines
    log_file = repository / LOG_SUFFIX
    if log_file.is_file():
        log_data_lines = log_file.read_text().splitlines()
        print("## Last 5 log lines:")
        for line in log_data_lines[-5:]:
            print(line)
    else:
        print("## Action log ('./cricic/log') not present")


def remove(repository, **_):
    """ Remove cricic-related files """
    remove_confirm = input("Remove cricic files? [y/n] ")
    remove_repo = remove_confirm.lower() in ('y', 'yes')
    if not remove_repo:
        return

    repo_conf_dir = repository / 'cricic'

    # Remove hooks
    for hook in HOOKS:
        (repository / 'hooks' / hook).unlink()

    # Remove conf dir contents
    for file_ in repo_conf_dir.glob('*'):
        file_.unlink()

    repo_conf_dir.rmdir()
