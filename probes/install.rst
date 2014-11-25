Installation
------------

**Probes** can be installed either on GNU/Linux and on Microsoft Windows
systems. The installation procedure may differs between the two systems.

.. _probe-install-source:

Installation from source
````````````````````````

According to the system that host the analyzers, the procedure to install the
python-based application for **Probes** may differ. This section describes how
to get the source code of the application and to install it on your preferred
system.

Downloading the source code from `github.com <https://github.com/quarkslab/irma-probe>`_
****************************************************************************************

The source code is hosted on github.com. One can fetch an up-to-date version
with the following commands. Let us note that there is a common submodule named
``irma-common`` that could be fetched automatically with the ``--recursive``
option:

.. code-block:: bash

    $ git clone --recursive https://github.com/quarkslab/irma-probe

Building the source distribution
********************************

We provide a ``Makefile`` that helps to build the python source distribution. By
default, the source distribution will be available in the ``dist/`` directory.
The created archive will be used to install the application.

.. code-block:: bash

    $ make source
    $ ls dist/
    irma-probe-app-1.1.0.tar.gz

.. note:: Required tools to build the source distribution

    Few tools are needed to build the python source distribution and to install
    the application:

    * make
    * python-pip
    * python-setuptools

Once the source distribution is built, one can install it either on a Microsoft
Windows or a GNU/Linux system.

Installing the source distribution
**********************************

To be able to install the python source distribution, we assume that you have
already installed the following software on your system. The prerequisites are
recalled here.

Prerequisites
+++++++++++++

We assume that you have a command line interface on your system [#]_ with
the following tools installed:

* python 2.7.x (see `Python for Windows <https://www.python.org/downloads/windows/>`_ 
  for prebuild MSI installer)
* python-pip (see `Install pip <https://pip.pypa.io/en/latest/installing.html>`_ 
  for the recommended way to install pip package manager)

Furthermore, we assume that you have created an user ``irma`` that will be used
to run the python application.

.. note:: On GNU/Linux, one can create the user (and the group) ``irma`` with:

    .. code-block:: bash

        $ sudo adduser --system --no-create-home --group irma


Installation on Microsoft Windows
+++++++++++++++++++++++++++++++++

On windows system, we will assume that the code for the **Probe** will be
installed at the root of the ``C:\`` drive, namely in ``C:\irma\irma-probe``.

Due to differences between Python for Windows and Python for Linux, the
installation with pip can only be done with the following command:

.. code-block:: bat

    $ C:\Python27\Scripts\pip.exe install irma-probe-app-1.0.4.tar.gz --root="C:\irma\irma-probe" 

However, this command puts the code source in ``C:\irma\irma-probe\Python27``
instead of ``C:\irma\irma-probe``. To fix this, either install
``irma-probe-app`` with ``pip`` and move the content of
``C:\irma\irma-probe\Python27`` to ``C:\irma\irma-probe\`` or simply copy the
code source you have just checked out from github.com in
``C:\irma\irma-probe``. Both methods should work.

Since the way we packaged the python application does not support
automatic installation of dependencies, we need to install them manually:

.. code-block:: bat

    $ C:\Python27\Scripts\pip.exe install -r C:\irma\irma-probe\requirements.txt
    [...]


Installation on GNU/Linux
+++++++++++++++++++++++++

On GNU/Linux system, we will assume that the code for the **Probe** will be
installed in ``/opt/irma/irma-probe`` directory.

.. code-block:: bash

    $ pip install irma-probe-app-1.1.0.tar.gz --install-option="--install-base=/opt/irma/irma-probe" 
    [...]

Since the way we packaged the python application does not so support
automatic installation of dependencies, we need to install them manually:

.. code-block:: bash

    $ pip install -r /opt/irma/irma-probe/requirements.txt
    [...]

If everything has gone well, the python application is now installed
on your system. The next step is to configure it for your platform and to
enable the analyzers you need.

.. rubric:: Footnotes

.. [#] On Microsoft Windows, a Linux-like lightweight command line
       interface can be installed by installing 
       `MSYS <http://www.mingw.org/wiki/MSYS>`_.
