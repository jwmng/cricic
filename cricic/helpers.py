import logging
import subprocess as sp

LOG_SUFFIX = 'cricic/cricic.log'


def _get_log_path(repository):
    return (repository / LOG_SUFFIX).resolve()


def _is_git_repo(dir_):
    if not dir_.is_dir():
        return False
    try:
        sp.check_call(('git', 'rev-parse', '--git-dir'), cwd=dir_,
                      stderr=sp.PIPE, stdout=sp.PIPE)
        return True
    except sp.CalledProcessError:
        return False


def _log(repository, lvl_name, msg):
    log_file = _get_log_path(repository)
    logging.basicConfig(level=logging.INFO, filename=str(log_file),
                        format="%(asctime)s %(levelname)s %(message)s",
                        datefmt="%Y-%m-%d %H:%M")
    level = getattr(logging, lvl_name, logging.INFO)
    logging.log(level, msg)
