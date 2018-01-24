Installation
------------

**Probes** can be installed either on GNU/Linux and on Microsoft Windows
systems. The installation procedure may differs between the two systems.

.. _probe-install-source:

Downloading the source code from `github.com <https://github.com/quarkslab/irma>`_
**********************************************************************************

The source code is hosted on github.com. One can fetch an up-to-date version
with the following commands. Let us note that there is a common submodule named
``common`` that is a soft-link (``lib``), do not forget the ``dereference``
option of ``cp`` [#]_ (``-L``):


.. code-block:: bash

    # If src repository not already cloned
    $ git clone https://github.com/quarkslab/irma /opt/irma/src
    $ cp -rL /opt/irma/src/probe /opt/irma/irma-probe/current

We assume that you have a command line interface on your system with
the following tools installed:

* python 3.4.x and newer on Linux
* python 3.5.x and newer on Windows (see `Python for Windows <https://www.python.org/downloads/windows/>`_
  for prebuild MSI installer)
* python3-pip (see `Install pip <https://pip.pypa.io/en/latest/installing.html>`_
  for the recommended way to install pip package manager)

Furthermore, we assume that you have created an user ``irma`` that will be used
to run the python application.

.. note:: On GNU/Linux, one can create the user (and the group) ``irma`` with:

    .. code-block:: bash

        $ sudo adduser --system --no-create-home --group irma


Installation on Microsoft Windows
+++++++++++++++++++++++++++++++++

On windows system, we will assume that the code for the **Probe** will be
installed at the root of the ``C:\`` drive, namely in ``C:\irma\irma-probe\current``.


.. code-block:: none

    $ C:\Python27\Scripts\pip.exe install virtualenv
    $ C:\Python27\Scripts\virtualenv C:\irma\irma-probe\current\venv


.. code-block:: none

    $ cd C:\irma\irma-probe\current\
    $ .\venv\Scripts\pip.exe install -r requirements.txt
    [...]


Installation on GNU/Linux
+++++++++++++++++++++++++

On GNU/Linux system, we will assume that the code for the **Probe** will be
installed in ``/opt/irma/irma-probe/current`` directory.

The source code is hosted on github.com. One can fetch an up-to-date version
with the following commands. Let us note that there is a common submodule named
``common`` that is a soft-link (``lib``), do not forget the ``dereference``
option of ``cp`` (``-L``):


.. code-block:: bash

    # If src repository not already cloned
    $ git clone https://github.com/quarkslab/irma /opt/irma/src
    $ cp -rL /opt/irma/src/probe /opt/irma/irma-probe/current

We need few dependencies for future steps:

    $ sudo apt-get install python3-virtualenv python3-dev


then, we need to install python dependencies manually in a virtualenv :

.. code-block:: bash

    $ virtualenv --system-site-packages --python=/usr/bin/python3 /opt/irma/irma-probe/current/venv
    $ /opt/irma/irma-probe/current/venv/bin/pip install -r /opt/irma/irma-probe/current/requirements.txt
    [...]


If everything has gone well, the python application is now installed
on your system. The next step is to configure it for your platform and to
enable the analyzers you need.

.. rubric:: Footnotes

.. [#] On Microsoft Windows, a Linux-like lightweight command line
       interface can be installed by installing
       `MSYS <http://www.mingw.org/wiki/MSYS>`_ or Git for windows.
