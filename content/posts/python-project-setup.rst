==================================
Setting up a modern Python project
==================================

:date: 2019-04-02
:category: development
:tags: python, testing, unittest, CI

Recently I've been working on a new Python-based project, using Python 3.6.

Having the opportunity for a fresh start, I spent some time taking a look at
how to best make use of the the modern tools for project setup, testing, static
checking and so on, and how to integrate them nicely into Continuous
Integration systems (e.g. Travis_).

As a result I've also started updating my personal projects using the same
setup, and updated my `Python skeleton project`_ accordingly, so that it's easy
to apply it to new projects as well.

The main goals I've been pursuing in working on this setup are:

- dependencies should be declared in a single place
- use standard Python tooling (e.g., avoid the need for a Makefile)
- use the same setup in development and CI


The basics: ``setup.py``
------------------------

The ``setup.py`` file is the entry point for a Python project, so let's start
from there.

Aside from the usual boilerplate, the most importating thing here is to keep
track of install and test (and possibly development) dependencies
separately. It's quite common in projects to have an ``extra_require`` entry
called ``"testing"``, so that test dependencies can be installed via

.. code:: shell

   pip install .[testing]


In the end the ``setup.py`` will look like this:

.. code:: python

   from setuptools import (
       find_packages,
       setup,
   )


   tests_require = ['pytest', ...] # ... other test-specific dependencies

   config = {
       'name': 'myproject',
       'version': '0.0.1',
       # ... description, author details, and other metadata
       'packages': find_packages(include=['myproject', 'myproject.*']),
       'install_requires': [...],  # ... runtime dependencies
       'tests_require': tests_require,
       'extras_require': {'testing': tests_require},
   }


   setup(**config)

Note that this also uses the standard ``tests_require`` keyword, so that
``python setup.py test`` would also install test dependences.


Running ``tox``
---------------

Tox_ is a very nice tool for setting up and running commands in separate
virtualenvs, with different set of dependencies.

In my setup, I use ``tox`` for running everything, thus eliminating the need
for ``make`` and makefiles.

``tox`` is configured using a ``tox.ini`` file at the root of the project.
It basically contains rules for the following stages:

- formatting
- linting
- static type checking
- running unit tests (with coverage report)
- (optionally) building documentation

Each target tracks its dependencies independently, so that they're only
installed where really needed.


Formatting and linting
~~~~~~~~~~~~~~~~~~~~~~

The formatting and linting stages use Yapf_ and isort_ (for sorting imports);
finally, linting also runs Flake8_.

Both ``yapf`` and ``isort`` have their own config files which allows tweaking
the desired format.

The formatting stage actually updates files, while the linting one just ensure
source code conforms to the formatting conventions:

.. code:: ini

   [globals]
   lint_files = setup.py myproject

   [testenv:format]
   deps =
       isort
       yapf
   commands =
       {envbindir}/yapf --in-place --recursive {[globals]lint_files}
       {envbindir}/isort --recursive {[globals]lint_files}

   [testenv:lint]
   deps =
       flake8
       isort
       yapf
   commands =
       {envbindir}/yapf --diff --recursive {[globals]lint_files}
       {envbindir}/isort --check-only --diff --recursive {[globals]lint_files}
       {envbindir}/flake8 {[globals]lint_files}


Static type checking
~~~~~~~~~~~~~~~~~~~~

Starting from version 3.6, Python supports variables annotations (PEP-526_) in
addition to type annotations in function declarations.

This allows static type checking of code using these declarations, which can be
done with mypy_.

This can be easily run from ``tox`` with the following stage:

.. code:: ini

   [testenv:check]
   deps =
       mypy
   commands =
       {envbindir}/mypy -p myproject {posargs}


Running tests
~~~~~~~~~~~~~

Finally, but actually most importantly, we want to run tests on our code.

I use pytest_ in most my projects both as framework for writing tests and as
test runner.  It is fully compatible with tests based on the ``unittest``
framework, so it can also be used just as a runner for existing test suites.

In addition to running tests, I also want to ensure the code 100%
test-covered. ``pytest`` supports generating coverage reports through the
``pytest-cov`` plugin.

.. code:: ini

   [testenv:coverage]
   deps =
       .
       .[testing]
       pytest-cov
   commands =
       {envbindir}/pytest --cov {posargs}


Note that we're installing project test dependencies with ``.[testing]`` as
mentioned above.

With this setup, we just need to run tox with the desired stages, such as:

.. code:: shell

   tox -e format,lint,check,coverage


Note that test stages pass ``{posargs}`` to ``pytest``, which allows, for
instance, limiting runs to a set of files, or making the output verbose:

.. code:: shell

   tox -e coverage -- -vs


CI setup
--------

Using a public CI system (such as Travis_), we can get test runs at every repository push.

With ``tox`` properly set up with different targets, the setup is pretty straightforward.

We can use Travis' "stages" to run each step individually:

.. code:: yaml

   language: python
   python:
     - "3.6"
     - "3.7-dev"
   matrix:
     fast_finish: true
   stages:
     - lint
     - check
     - test
   install: pip install tox codecov
   jobs:
     include:
       - stage: lint
         script: tox -e lint
         python: "3.6"
       - stage: check
         script: tox -e check
         python: "3.6"
   script: tox -e coverage
   after_success: codecov


This way, failures are reported nicely at the proper stage (lint, check or
test).

The configuration shown above also pushes coverage results to Codecov_ so that
coverage changes can also be tracked.

... and that's it!


.. _`Python skeleton project`: https://github.com/albertodonato/python-skeleton
.. _Tox: https://tox.readthedocs.io/
.. _Travis: https://travis-ci.com/
.. _Yapf: https://pypi.org/project/yapf
.. _isort: https://pypi.org/project/isort
.. _Flake8: https://pypi.org/project/flake8
.. _mypy: http://mypy-lang.org/
.. _PEP-526: https://www.python.org/dev/peps/pep-0526/
.. _pytest: https://docs.pytest.org/en/latest/
.. _Codecov: https://codecov.io/
