pretix-banktool
===============

This is a command-line tool for `pretix`_ that allows you to automatically query your bank account and sync
transaction data to a pretix server. This uses an API provided by pretix version 1.5 or newer.

Current limitations:

* Currently limited to banks implementing the FinTS protocol (formerly HBCI), which is mostly availabile with Germany
  banks.

* Only supports PIN/TAN authentication, no chip cards.

* Currently only supports uploading bank transactions on a per-organizer level, not on a per-event level.

**Currently, this tool stores your banking PIN in plain text on disk or ask you any time. We advise you to use a
read-only banking login or strong two-factor-auth for transactions. We will add support for system keyrings at a
later point in time.**

Installation and usage
----------------------

First, make sure you have a recent Python installation on your system. If ``python -V`` gives you a version 2.x,
try using ``python3`` instead or install a newer Python. We recommend Python 3.11+, but 3.9+ should work as well.

Then, we recommend creating a virtual environment to isolate the python dependencies of this package from other
python programs ony our system::

    $ pyvenv env
    $ source env/bin/activate

You should now see a ``(env)`` prepended to your shell prompt. You have to do this
in every shell you use to work with pretix (or configure your shell to do so
automatically). Depending on your Python version, you might need to replace ``pyvenv`` with ``python -m venv``.
If you are working on Ubuntu or Debian, we recommend upgrading your pip and setuptools installation inside
the virtual environment::

    (env)$ pip3 install -U pip setuptools

Now you can install the bank tool::

    (env)$ pip3 install pretix-banktool

To configure it, run the following command::

    (env)$ pretix-banktool setup

You will be asked a number of questions on your online banking access as well as for the URL of your pretix
installation and your API key. The prompt will also tell you how to obtain that API key.

At the end, this command will write a config file to a location of your choice. You need to specify this config file
for all further actions. The command::

    (env)$ pretix-banktool test configfile-path.cfg

will test both the connection to the bank as well as the connection to pretix, but will not perform any actions. To
actually upload data, use::

    (env)$ pretix-banktool upload --days 30 configfile-path.cfg

The ``--days`` option specifies the timeframe of transaction to fetch from the bank. If you omit it, the tool will
fetch the last 30 days.

Go to the "Import bank data" tab of the organizer settings in pretix to view any transactions that could not be
automatically assigned to a ticket order.

Contributing
------------

If you like to contribute to this project, you are very welcome to do so. If you have any
questions in the process, please do not hesitate to ask us.

Please note that we have a `Code of Conduct`_ in place that applies to all project contributions, including issues,
pull requests, etc.

License
-------

Copyright 2017 Raphael Michel

Released under the terms of the GNU General Public License v3.0.

.. _pretix: https://github.com/pretix/pretix
.. _Code of Conduct: https://docs.pretix.eu/en/latest/development/contribution/codeofconduct.html
