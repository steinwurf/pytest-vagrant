#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import shutil
import hashlib
import subprocess

from waflib.Configure import conf
from waflib import Logs

import waflib

top = '.'

VERSION = '0.0.0'

from waflib.Build import BuildContext
class UploadContext(BuildContext):
        cmd = 'upload'
        fun = 'upload'


def resolve(ctx):

    # Testing dependencies
    ctx.add_dependency(
        name='virtualenv',
        recurse=False,
        optional=False,
        resolver='git',
        method='checkout',
        checkout='15.1.0',
        sources=['github.com/pypa/virtualenv.git'])

def options(opt):

    opt.add_option(
        '--run_tests', default=False, action='store_true',
        help='Run all unit tests')

    opt.add_option(
        '--pytest_basetemp', default='pytest_temp',
        help='Set the basetemp folder where pytest executes the tests')


def _create_virtualenv(ctx, cwd):
    # Make sure the virtualenv Python module is in path
    venv_path = ctx.dependency_path('virtualenv')

    env = os.environ.copy()
    env.update({'PYTHONPATH': os.path.pathsep.join([venv_path])})

    from waflib.extras.wurf.virtualenv import VirtualEnv
    return VirtualEnv.create(cwd=cwd, env=env, name=None, ctx=ctx, overwrite=False)


def build(bld):

    # Create a virtualenv in the source folder and build universal wheel
    venv = _create_virtualenv(cwd=bld.path.abspath(), ctx=bld)

    with venv:
        venv.pip_install(['wheel'])
        venv.run('python setup.py bdist_wheel --universal')

    # Delete the egg-info directory, do not understand why this is created
    # when we build a wheel. But, it is - perhaps in the future there will
    # be some way to disable its creation.
    egg_info = os.path.join(bld.path.abspath(), 'pytest_vagrant.egg-info')

    if os.path.isdir(egg_info):
        waflib.extras.wurf.directory.remove_directory(path=egg_info)

    # Run the unit-tests
    if bld.options.run_tests:
        _pytest(bld=bld)


def _find_wheel(ctx):
    """ Find the .whl file in the dist folder. """

    wheel = ctx.path.ant_glob('dist/*-'+VERSION+'-*.whl')

    if not len(wheel) == 1:
        ctx.fatal('No wheel found (or version mismatch)')
    else:
        wheel = wheel[0]
        Logs.info('Wheel %s', wheel)
        return wheel


def upload(bld):
    """ Upload the built wheel to PyPI (the Python Package Index) """

    venv = _create_virtualenv(cwd=bld.bldnode.abspath(), ctx=bld)

    with venv:
        venv.pip_install('twine')

        wheel = _find_wheel(ctx=bld)

        venv.run('python -m twine upload {}'.format(wheel))


def _pytest(bld):

    # Create the virtualenv in the build folder to make sure we run
    # isolated from the sources
    venv = _create_virtualenv(cwd=bld.bldnode.abspath(), ctx=bld)
    with venv:
        # with venv:
        venv.pip_install(['pytest', 'paramiko'])

        # Install the pytest-vagrant plugin in the virtualenv
        wheel = _find_wheel(ctx=bld)

        venv.run('python -m pip install {}'.format(wheel))

        # Added our systems path to the virtualenv (otherwise we cannot
        # find vagrant)
        venv.env['PATH'] = os.path.pathsep.join([venv.env['PATH'], os.environ['PATH']])

        # We override the pytest temp folder with the basetemp option,
        # so the test folders will be available at the specified location
        # on all platforms. The default location is the "pytest" local folder.
        basetemp = os.path.abspath(os.path.expanduser(
            bld.options.pytest_basetemp))

        # We need to manually remove the previously created basetemp folder,
        # because pytest uses os.listdir in the removal process, and that fails
        # if there are any broken symlinks in that folder.
        if os.path.exists(basetemp):
            waflib.extras.wurf.directory.remove_directory(path=basetemp)

        testdir = bld.path.find_node('test')

        # Make python not write any .pyc files. These may linger around
        # in the file system and make some tests pass although their .py
        # counter-part has been e.g. deleted
        command = 'python -B -m pytest {} --basetemp {}'.format(
            testdir.abspath(), basetemp)


        if bld.options.verbose:
            command += " --capture=no"

        venv.run(command)