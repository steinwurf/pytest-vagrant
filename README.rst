============
Introduction
============

|PyPi| |Waf Python Tests| |Black| |Flake8| |Pip Install|

.. |PyPi| image:: https://badge.fury.io/py/pytest-vagrant.svg
    :target: https://badge.fury.io/py/pytest-vagrant

.. |Waf Python Tests| image:: https://github.com/steinwurf/pytest-vagrant/actions/workflows/python-waf.yml/badge.svg
   :target: https://github.com/steinwurf/pytest-vagrant/actions/workflows/python-waf.yml

.. |Flake8| image:: https://github.com/steinwurf/pytest-vagrant/actions/workflows/flake.yml/badge.svg
    :target: https://github.com/steinwurf/pytest-vagrant/actions/workflows/flake.yml

.. |Black| image:: https://github.com/steinwurf/pytest-vagrant/actions/workflows/black.yml/badge.svg
      :target: https://github.com/steinwurf/pytest-vagrant/actions/workflows/black.yml

.. |Pip Install| image:: https://github.com/steinwurf/pytest-vagrant/actions/workflows/pip.yml/badge.svg
      :target: https://github.com/steinwurf/pytest-vagrant/actions/workflows/pip.yml


pytest-vagrant provides a py.test fixture for working with vagrant
in pytest.

.. contents:: Table of Contents:
   :local:

Installation
============

To install pytest-vagrant::

    pip install pytest-vagrant

Usage
=====

To make it easy to use in with `pytest` the Vagrant object can be
injected into a test function by using the vagrant fixture.

Example::

    def test_run_fail(vagrant):
        machine = vagrant.from_box(
            box="hashicorp/bionic64", name="pytest_vagrant", reset=False)

        with machine.ssh() as ssh:
            ssh.run("some_command")

The ``vagrant`` argument is an instance of Vagrant and represents the
vagrant environment on the machine running the test code.


Release new version
===================

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
