pretix-banktool
===============

This is a command-line tool for `pretix`_ that allows you to automatically query your bank account and sync
transaction data to a pretix server.

**Currently, this tool stores your banking PIN in plain text on disk. We advise you to use a read-only banking login
or strong two-factor-auth for transactions. We will add support for system keyrings or password prompts later.**

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
