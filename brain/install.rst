Installation
------------

The **Brain** must be installed on a GNU/Linux distribution. With some efforts,
it should be possible to run it on a Microsoft Windows system, but this has not
been tested yet.

.. _brain-install-source:

Installation from source
````````````````````````

This section describes how to get the source code of the application for the
**Brain** and to install it.

Downloading the source code from `github.com <https://github.com/quarkslab/irma-brain>`_
****************************************************************************************

The source code is hosted on github.com. One can fetch an up-to-date version
with the following commands. Let us note that there is a common submodule named
``irma-common`` that could be fetched automatically with the ``--recursive``
option:

.. code-block:: bash

    $ git clone --recursive https://github.com/quarkslab/irma-brain

Building the source distribution
********************************

We provide a ``Makefile`` that helps to build the python source distribution. By
default, the source distribution will be available in the ``dist/`` directory.
The created archive will be used to install the application.

.. code-block:: bash

    $ make source
    $ ls dist/
    irma-brain-app-1.0.4.tar.gz

.. note:: Required tools to build the source distribution

    Few tools are needed to build the python source distribution and to install
    the application:

    * make
    * python-pip
    * python-setuptools

Installing the source distribution
**********************************

To be able to install the python source distribution, we assume that you have
already install the following software on your system. The pre-requisites are
recalled here.

Pre-requisites
++++++++++++++

We assume that you have a command line interface on your system with
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

Installation on GNU/Linux
+++++++++++++++++++++++++

On GNU/Linux system, we will assume that the code for the **Brain** will be
installed in ``/opt/irma/irma-brain`` directory, which is the configured default
installation directory.

.. code-block:: bash

    $ pip install --install-option="--install-base=/opt/irma/irma-brain" irma-brain-app-1.1.0.tar.gz
    [...]

Since the way we packaged the python application does not so support
automatic installation of dependencies, we need to install them manually:

.. code-block:: bash

    $ pip install -r /opt/irma/irma-brain/requirements.txt
    [...]

If everything has gone well, you should have installed the python application
on your system. The next step is to install the other components it relies on
and finally to configure it for your platform.
