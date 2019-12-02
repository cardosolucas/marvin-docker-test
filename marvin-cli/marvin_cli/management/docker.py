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

import click
import os
import docker
import subprocess

from .._compatibility import iteritems
from .._logging import get_logger


logger = get_logger('management.docker')


@click.group('docker')
def cli():
    pass

COMMANDS = {
    'notebook': 'notebook --allow-root',
    'dryrun': 'engine-dryrun',
    'test' : 'test',
    'httpserver': 'engine-httpserver -h 0.0.0.0 -p 8000 --executor-path /opt/marvin/data/marvin-engine-executor-assembly-0.0.5.jar'
}

def stop_engine(engine):
    client = docker.from_env()
    container = client.containers.get(engine + '-run')
    container.stop()
    container.remove()

def run_container(memory, cpu, engine, command, benchmark):
    client = docker.from_env()
    try:
        image = client.images.get(engine)
        image.remove()
    except:
        pass
    print("Criando imagem da engine {}...".format(engine))
    work_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'engine_develop', 'engine-commands')
    client.images.build(
        path = work_dir,
        tag = engine,
        nocache=True,
        forcerm=True,
        buildargs = {
            'ENGINE_NAME': engine,
            'COMMAND': COMMANDS[command]
        }
    )
    print("Criando container da engine {}...".format(engine))
    container = client.containers.run(
        image = engine,
        name = engine + '-run',
        stdout = True,
        stderr = True,
        tty = True,
        stream = True,
        detach = True,
        mem_limit = memory,
        cpuset_cpus = cpu,
        volumes = {
            os.environ['MARVIN_HOME']: {
                'bind' : '/opt/marvin',
                'mode' : 'rw'
            }
        },
        ports = {
            '8888/tcp': 8888,
            '8000/tcp': 8000
        }
    )
    try:
        if not benchmark:
            for line in container.logs(stream=True):
                print(line.decode(), end = '')
        else:
            os.system("docker stats " + engine + "-run")
    except KeyboardInterrupt:
        pass
    stop_engine(engine)

@cli.command('docker-develop', help='Marvin Engine Generate - Build marvin engine in a container')
@click.option('--memory', '-m', help='Memory quota', default='2g')
@click.option('--cpu', '-c', help='CPU quota', default='0-2')
@click.option('--engine', '-e', help='Engine model file path')
@click.option(
    '--command',
    '-cmd',
    default='notebook',
    type=click.Choice(['notebook', 'dryrun', 'test', 'httpserver']),
    help='Command to be sent to container')
@click.pass_context
def generate(ctx, memory, cpu, engine, command):
    run_container(memory, cpu, engine, command, benchmark=False)

@cli.command('docker-stop', help='Stop Container - Stop development container')
@click.option('--engine', '-e', help='Engine Container to be stopped')
@click.pass_context
def stop(ctx, engine):
    stop_engine(engine)

@cli.command('docker-benchmark', help='Marvin Docker Benchmark - Run marvin benchmark in a container')
@click.option('--memory', '-m', help='Memory quota', default='2g')
@click.option('--cpu', '-c', help='CPU quota', default='0-2')
@click.option('--engine', '-e', help='Engine model file path', type=click.Path(exists=True))
@click.pass_context
def benchmark(ctx, memory, cpu, engine):
    run_container(memory, cpu, "santander-customer-engine", "dryrun", True)