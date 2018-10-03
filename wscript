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

VERSION = '1.0.0'

from waflib.Build import BuildContext


class UploadContext(BuildContext):
    cmd = 'upload'
    fun = 'upload'


def options(opt):

    opt.add_option(
        '--run_tests', default=False, action='store_true',
        help='Run all unit tests')

    opt.add_option(
        '--pytest_basetemp', default='pytest_temp',
        help='Set the basetemp folder where pytest executes the tests')


def configure(conf):

    # Check if we have vagrant installed, needed to run the mininet
    # tests
    conf.find_program('vagrant', mandatory=False)

    # Check if we have VirtualBox installed, needed to run the mininet
    # tests
    conf.find_program('VBoxManage', mandatory=False)


def build(bld):

    # Create a virtualenv in the source folder and build universal wheel
    venv = bld.create_virtualenv(cwd=bld.path.abspath(), overwrite=False)

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

    venv = bld.create_virtualenv(cwd=bld.bldnode.abspath())

    with venv:
        venv.pip_install(['twine'])

        wheel = _find_wheel(ctx=bld)

        venv.run('python -m twine upload {}'.format(wheel))


def _pytest(bld):

    if not bld.env.VAGRANT:
        bld.fatal("Cannot run pytest-vagrant tests without vagrant installed.")

    if not bld.env.VBOXMANAGE:
        bld.fatal("Cannot run pytest-vagrant tests without VirtualBox installed.")

    # Create the virtualenv in the build folder to make sure we run
    # isolated from the sources
    venv = bld.create_virtualenv(cwd=bld.bldnode.abspath())
    with venv:
        # with venv:
        venv.pip_install(['pytest', 'pytest_testdirectory', 'paramiko'])

        # Install the pytest-vagrant plugin in the virtualenv
        wheel = _find_wheel(ctx=bld)

        venv.run('python -m pip install {}'.format(wheel))

        # Added our systems path to the virtualenv (otherwise we cannot
        # find vagrant)
        venv.env['PATH'] = os.path.pathsep.join(
            [venv.env['PATH'], os.environ['PATH']])

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
        command = 'python -B -m pytest {} --basetemp {} --vagrantfile {} --vagrantreset'.format(
            testdir.abspath(), basetemp, bld.path.abspath())

        if bld.options.verbose:
            command += " --capture=no"

        venv.run(command)
