import jinja2
import six
import shutil
import os
import sys
import re
import click
from unidecode import unidecode
import subprocess

from .._compatibility import iteritems
from .._logging import get_logger

logger = get_logger('management.engine')


@click.group('engine')
def cli():
    pass


TEMPLATE_BASES = {
    'python-engine': os.path.join(os.path.dirname(__file__), 'templates', 'python-engine'),
    'automl-engine': os.path.join(os.path.dirname(__file__), 'templates', 'python-engine'),
}

RENAME_DIRS = [
    ('project_package', '{{project.package}}'),
]

IGNORE_DIRS = [
    # Ignore service internal templates
    'templates'
]


_orig_type = type


@cli.command('engine-generate', help='Generate a new marvin engine project and install default requirements.')
@click.option('--name', '-n', prompt='Project name', help='Project name')
@click.option('--description', '-d', prompt='Short description', default='Marvin engine', help='Library short description')
@click.option('--mantainer', '-m', prompt='Mantainer name', default='Marvin AI Community', help='Mantainer name')
@click.option('--email', '-e', prompt='Mantainer email', default='dev@marvin.apache.org', help='Mantainer email')
@click.option('--package', '-p', default='', help='Package name')
@click.option('--dest', '-d', envvar='MARVIN_HOME', type=click.Path(exists=True), help='Root folder path for the creation')
@click.option('--no-git', is_flag=True, default=False, help='Don\'t initialize the git repository')
@click.option('--automl', '-aml', default='n' ,prompt='Use AutoML?: ', type=click.Choice(['y','n']))
@click.option('--python', '-py', default='python', help='The Python interpreter to use to create the new environment')
def generate(name, description, mantainer, email, package, dest, no_git, automl, python):
    type_ = 'python-engine'
    type = _orig_type


    # Check if package should be automl
    if automl == 'y':
        type_ = 'automl-engine'
        
    # Process package name
    package = _slugify(package or name)

    # Make sure package name starts with "marvin"
    if not package.startswith('marvin'):
        package = 'marvin_{}'.format(package)

    # Remove "lib" prefix from package name
    if type_ == 'lib' and package.endswith('lib'):
        package = package[:-3]
    # Custom strip to remove underscores
    package = package.strip('_')

    # Append project type to services

    if type_ in TEMPLATE_BASES and not package.endswith('engine'):
        package = '{}_engine'.format(package)

    # Process directory/virtualenv name

    # Directory name should use '-' instead of '_'
    dir_ = package.replace('_', '-')

    # Remove "marvin" prefix from directory
    if dir_.startswith('marvin'):
        dir_ = dir_[6:]
    dir_ = dir_.strip('-')

    # Append "lib" to directory name if creating a lib
    if type_ == 'lib' and not dir_.endswith('lib'):
        dir_ = '{}-lib'.format(dir_)

    dest = os.path.join(dest, dir_)

    if type_ not in TEMPLATE_BASES:
        print('[ERROR] Could not found template files for "{type}".'.format(type=type_))
        sys.exit(1)

    project = {
        'name': _slugify(name),
        'description': description,
        'package': package,
        'toolbox_version': os.getenv('TOOLBOX_VERSION'),
        'type': type_
    }

    mantainer = {
        'name': mantainer,
        'email': email,
    }

    context = {
        'project': project,
        'mantainer': mantainer,
    }

    folder_created = False

    try:
        _copy_scaffold_structure(TEMPLATE_BASES[type_], dest)

        folder_created = True

        _copy_processed_files(TEMPLATE_BASES[type_], dest, context)
        _rename_dirs(dest, RENAME_DIRS, context)
        _make_data_link(dest)

        if not no_git:
            _call_git_init(dest)

        print('\nDone!!!!')

    except Exception as e:
        logger.info(e)
        print(e)
        # remove project if created
        if os.path.exists(dest) and folder_created:
            shutil.rmtree(dest)


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def _slugify(text, delim='_'):
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return six.u(delim.join(result))


def _copy_scaffold_structure(src, dest):
    os.mkdir(dest)

    for root, dirs, files in os.walk(src):
        for dir_ in dirs:
            dirname = os.path.join(root, dir_)
            dirname = '{dest}{dirname}'.format(dest=dest, dirname=dirname.replace(src, ''))  # get dirname without source path

            os.mkdir(dirname)


def _copy_processed_files(src, dest, context):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(src))

    print('Processing template files...')

    for root, dirs, files in os.walk(src):

        dirname = root.replace(src, '')[1:]  # get dirname without source path
        to_dirname = os.path.join(dest, dirname)

        should_process = not any(root.startswith(dir_) for dir_ in IGNORE_DIRS)

        for file in files:

            # Ignore trash
            if file == '.DS_Store' or file.endswith('.pyc'):
                continue

            from_ = os.path.join(dirname, file)
            to_ = os.path.join(to_dirname, file)

            print('Copying "{0}" to "{1}"...'.format(from_, to_))

            if not should_process:
                shutil.copy(os.path.join(src, from_), to_)
            else:
                template = env.get_template(from_)
                output = template.render(**context)

                with open(to_, 'w') as file:
                    file.write(output)


def _rename_dirs(base, dirs, context):
    for dir_ in dirs:
        dirname, template = dir_
        oldname = os.path.join(base, dirname)

        processed = jinja2.Template(template).render(**context)
        newname = os.path.join(base, processed)

        shutil.move(oldname, newname)

        print('Renaming {0} as {1}'.format(oldname, newname))


def _call_git_init(dest):
    command = ['bash', '-c', '/usr/bin/git init {0}'.format(dest)]
    print('Initializing git repository...')
    try:
        subprocess.Popen(command, env=os.environ).wait()
    except OSError:
        print('WARNING: Could not initialize repository!')


def _make_data_link(dest):
    data_path = os.environ['MARVIN_DATA_PATH']
    data_link = os.path.join(dest, 'notebooks/data')
    os.symlink(data_path, data_link)