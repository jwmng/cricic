"""
Hooks file for cricic

The hook functions `pre_receive` and `post_receive` run when called from
`__main__`.
This happens when the corresponding git hooks are executed.
"""

import sys
import subprocess as sp
from configparser import ConfigParser
from pathlib import Path

from cricic.constants import CONF_LOCATIONS


def _leftpad(raw, chars='\t'):
    return '\n'.join(chars + line for line in raw.splitlines())


def _get_config(repository, config):
    """ Read global configs, then override with local config """
    confp = ConfigParser()
    for config_path in CONF_LOCATIONS:
        confp.read(config_path / 'config.ini')

    local_config = Path(repository) / 'cricic/config.ini'
    confp.read(local_config)
    confp.read(config)
    return confp


def _make_targets(repository, confp, stage, cwd='.', dry_run=False):
    """
    - Find buildfile path configured in `confp` in `repository`
    - Run the space-separated `make` targets in `cwd`
    """
    targets = confp.get(stage, 'targets').split(' ')

    for target in targets:
        # If no targets are specified, the first target will be the empty
        # string. In that case we skip building
        if not target:
            continue

        print("\n-- Stage: %s, Target: %s" % (stage.upper(), target.upper()))
        buildfile = Path(repository) / confp.get('general', 'buildfile')
        run_args = ['make', '-f', buildfile, target]
        if confp.getboolean(stage, 'silent'):
            run_args.append('-s')

        if dry_run:
            run_args.append('-n')

        make_proc = sp.run(run_args, stdout=sp.PIPE, stderr=sp.PIPE,
                           cwd=str(cwd))

        stdout = make_proc.stdout.decode('utf-8').strip()
        stderr = make_proc.stderr.decode('utf-8').strip()

        print(_leftpad(stdout, chars='    '))

        try:
            make_proc.check_returncode()
        except sp.CalledProcessError:
            print(_leftpad(stderr, chars='!!  '))
            print("-- Error in stage %s" % target.upper())
            return False

    return True


def pre_receive(repository, config, **_):
    """ Runs when receiving code, before accepting files """
    confp = _get_config(repository, config)

    # Sanity checks
    if not Path.is_dir(repository / 'cricic'):
        print("-- No cricic repository: did you initialise correctly?")
        sys.exit(1)

    if not Path.is_file(repository / 'cricic' / 'buildfile'):
        print("-- No buildfile: did you initialise correctly?")
        sys.exit(1)

    # Get targets
    success = _make_targets(repository, confp, 'pre')
    if not success:
        print("-- Rejecting push")
        sys.exit(1)


def post_receive(repository, config, **_):
    """ Runs after receiving code """
    confp = _get_config(repository, config)

    work_dir = Path(confp.get('repository', 'work_dir'))
    if not work_dir.is_absolute():
        work_dir = (repository / confp.get('repository', 'work_dir'))
    else:
        work_dir = work_dir.expanduser()

    work_dir = work_dir.resolve()

    # Checkout the files in the work dir
    if not work_dir.is_dir():
        work_dir.mkdir()
        print("!!  Created work dir %s" % str(work_dir))

    sp.run(('git',
            '--work-tree=' + str(work_dir),
            '--git-dir=' + str(repository),
            'checkout', '-q', '-f', str(confp.get('general', 'branch'))))

    # Copy new buildfile
    buildfile_update = (work_dir / '.cricicbuild')
    if buildfile_update.is_file():
        print("Updating buildfile")
        buildfile = Path(repository) / confp.get('general', 'buildfile')
        buildfile_old = buildfile.read_bytes()
        buildfile.write_bytes(buildfile_update.read_bytes())

        # Quick dry-run to prevent writing bad buildfile
        valid = _make_targets(repository, confp, 'pre', dry_run=True)
        if not valid:
            print("!!  Buildfile test failed")
            buildfile.write_bytes(buildfile_old)
            sys.exit(1)

        # Remove buildfile from production
        buildfile_update.unlink()

    success = _make_targets(repository, confp, 'post', cwd=work_dir)
    if not success:
        print("-- Cancelling further steps")
        sys.exit(1)
