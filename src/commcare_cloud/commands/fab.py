import os
import subprocess

from memoized import memoized

from commcare_cloud.cli_utils import print_command
from .command_base import CommandBase, Argument
from ..environment.paths import FABFILE
from six.moves import shlex_quote


class Fab(CommandBase):
    command = 'fab'
    help = (
        "Run a fab command as you would with fab"
    )

    arguments = (
        Argument(dest='fab_command', help="fab command", default=None, nargs="?"),
    )

    def modify_parser(self):

        class _Parser(self.parser.__class__):
            @property
            @memoized
            def epilog(self):
                return subprocess.check_output(['fab', '-f', FABFILE, '-l'])

        self.parser.__class__ = _Parser

    def run(self, args, unknown_args):
        cmd_parts = (
            'fab', '-f', FABFILE,
            args.env_name,
        ) + (
            (args.fab_command,) if args.fab_command else ()
        ) + tuple(unknown_args)
        cmd = ' '.join(shlex_quote(arg) for arg in cmd_parts)
        print_command(cmd)
        os.execvp('fab', cmd_parts)
