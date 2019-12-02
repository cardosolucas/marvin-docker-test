#!/usr/bin/env python
# coding=utf-8

# Copyright [2019] [Apache Software Foundation]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import os
import click

from .._compatibility import six
from .._logging import get_logger

from .docker import cli as cli_docker
from .engine import cli as cli_engine

__all__ = ['create_cli']


logger = get_logger('management')


VERSION_MSG = '''
  __  __            _____ __      __ _____  _   _       
 |  \/  |    /\    |  __ \\\ \    / /|_   _|| \ | |
 | \  / |   /  \   | |__) |\ \  / /   | |  |  \| | 
 | |\/| |  / /\ \  |  _  /  \ \/ /    | |  | . ` | 
 | |  | | / ____ \ | | \ \   \  /    _| |_ | |\  | 
 |_|  |_|/_/    \_\|_|  \_\   \/    |_____||_| \_| v%(version)s
'''


def create_cli():

    @click.group('custom')
    @click.option('--debug', is_flag=True, help='Enable debug mode.')
    @click.pass_context
    def cli(ctx, debug):
        ctx.obj = {
            'debug': debug
        }

    # Load internal commands
    commands = {}
    commands.update(cli_docker.commands)
    commands.update(cli_engine.commands)

    for name, command in commands.items():
        cli.add_command(command, name=name)

    # Add version and help messages
    from .. import __version__
    cli = click.version_option(version=__version__,
                               message=VERSION_MSG.replace('\n', '\n  '))(cli)

    cli.help = '\b{}\n'.format(VERSION_MSG % {'version': __version__})

    return cli
