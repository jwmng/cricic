#!/usr/bin/env python3

"""
Cricic main entry point.
Contains the CLI interface, delegates actual to `run` and `hooks`
"""

import sys
from argparse import ArgumentParser
from pathlib import Path

from cricic.run import init, info, remove, RunError
from cricic.hooks import pre_receive, post_receive


def _err(msg):
    print("ERROR:", msg)
    sys.exit(1)


def setup_parser():
    """ Build ourserveles an argument parser """
    aparser = ArgumentParser(
        prog='cricic',
        description='A tiny git-managed CI',
        epilog='See the README for more help',
        add_help=True
        )

    aparser.add_argument(
        'repository',
        help="Repository dir",
        nargs='?',
        default='.',
        type=Path
        )

    aparser.add_argument(
        '-c',
        '--config',
        help="Global configuration file location",
        default='~/.config/cricic/config.ini'
        )

    subparser = aparser.add_subparsers()

    sp_init = subparser.add_parser(
        'init',
        help="initialise a new cricic repository"
        )
    sp_info = subparser.add_parser(
        'info',
        help="show information about a repository"
        )

    sp_remove = subparser.add_parser(
        'remove',
        help="remove a repository"
        )

    sp_hook_post = subparser.add_parser(
        '@post-receive',
        help="run post-receive hook"
        )

    sp_hook_pre = subparser.add_parser(
        '@pre-receive',
        help="run pre-receive hook"
        )

    sp_init.set_defaults(func=init)
    sp_info.set_defaults(func=info)
    sp_remove.set_defaults(func=remove)
    sp_hook_pre.set_defaults(func=pre_receive)
    sp_hook_post.set_defaults(func=post_receive)

    return aparser


def main():
    """ Entry point """
    aparser = setup_parser()
    args = aparser.parse_args()
    try:
        fun = args.func
    except AttributeError:
        aparser.print_help()
        sys.exit(1)
    try:
        fun(**vars(args))
    except RunError as err:
        _err(err.msg)


if __name__ == '__main__':
    main()
