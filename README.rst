============
Introduction
============

.. image:: https://badge.fury.io/py/pytest-vagrant.svg
    :target: https://badge.fury.io/py/pytest-vagrant

pytest-vagrant provides a py.test fixture for working with vagrant
in pytest.

.. contents:: Table of Contents:
   :local:

Installation
===========

To install pytest-vagrant::

    pip install pytest-vagrant

Usage
=====

To make it easy to use in with py.test the Vagrant object can be
injected into a test function by using the vagrant fixture.

Example::

    def test_this_function(vagrant):
        if vagrant.status.not_created:
            vagrant.up()

The ``vagrant`` argument is an instance of Vagrant and represents the
vagrant environment on the machine running the test code.

You can pass your the path to your ``Vagrantfile`` by adding ``--vagrantfile``
when running py.test e.g.::

    python -m pytest test_directory --vagrantfile ../vagrant

One way to interace with the Vagrant VM is over ssh::

    def test_this_ssh(vagrant):

        with vagrant.ssh() as ssh:
            stdin, stdout, stderr = ssh.exec_command('ls -la')
            ...

An even easier way is to use the ``sshdirectory`` fixture for
running commands and working with files on the host::

    def test_this_dir(sshdirectory):

        testdir = sshdirectory.mkdir('test')
        testdir.run('touch hello_world.txt')
        assert testdir.contains_file('hello_world.txt')

        testdir.rmfile('hello_world.txt')
        assert not testdir.contains_file('hello_world.txt')

Relase new version
==================

1. Edit NEWS.rst and wscript (set correct VERSION)
2. Run ::

    ./waf upload

Source code
===========

The main functionality is found in ``src/vagrant.py`` and the
corresponding unit test is in ``test/test_vagrant.py`` if you
want to play/modify/fix the code this would, in most cases, be the place
to start.

Developer Notes
===============

We try to make our projects as independent as possible of a local system setup.
For example with our native code (C/C++) we compile as much as possible from
source, since this makes us independent of what is currently installed
(libraries etc.) on a specific machine.

To "fetch" sources we use Waf (https://waf.io/) augmented with dependency
resolution capabilities: https://github.com/steinwurf/waf

The goal is to enable a work-flow where running::

    ./waf configure
    ./waf build --run_tests

Configures, builds and runs any available tests for a given project, such that
you as a developer can start hacking at the code.

For Python project this is a bit unconventional, but we think it works well.

Tests
=====

The tests will run automatically by passing ``--run_tests`` to waf::

    ./waf --run_tests

This follows what seems to be "best practice" advise, namely to install the
package in editable mode in a virtualenv.

Notes
=====

* Why use an ``src`` folder (https://hynek.me/articles/testing-packaging/).
  tl;dr you should run your tests in the same environment as your users would
  run your code. So by placing the source files in a non-importable folder you
  avoid accidentally having access to resources not added to the Python
  package your users will install...
* Python packaging guide: https://packaging.python.org/distributing/
