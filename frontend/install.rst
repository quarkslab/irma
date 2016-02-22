Installation
------------

The **Frontend** must be installed on a GNU/Linux system. With some efforts, it
should be possible to run it on a Microsoft Windows system, but this has not
been tested yet.

This section describes how to get the source code of the application and to
install it.

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

On GNU/Linux system, we will assume that the code for the **Frontend** will be
installed in ``/opt/irma/irma-frontend`` directory, which is the configured default
installation directory.

The source code is hosted on github.com. One can fetch an up-to-date version
with the following commands. Let us note that there is a common submodule named
``irma-common`` that could be fetched automatically with the ``--recursive``
option:

.. code-block:: bash

    $ git clone --recursive https://github.com/quarkslab/irma-frontend /opt/irma/irma-frontend

then, we need to install python dependencies manually:

.. code-block:: bash

    $ pip install -r /opt/irma/irma-frontend/requirements.txt
    [...]

Building the web client
***********************

The first step that should be performed when installing the frontend from the
code source is to build the web client which is composed of static HTML files
mixed with javascript web framework (in particular, AngularJS).

One must install first some tools that are necessary to build the whole web
client:

.. code-block:: bash

    $ curl -sL https://deb.nodesource.com/setup | sudo bash -
    [...]
    $ sudo apt-get install -y nodejs
    [...]
    $ curl -sL https://www.npmjs.org/install.sh | sudo bash -
    [...]

Once the tools installed, you can build the static files for the web user
interface with the following commands, executed from the installation
directory:

.. code-block:: bash

    $ cd irma-frontend/web
    $ sudo npm install
    $ sudo node_modules/.bin/bower install --allow-root
    $ node_modules/.bin/gulp dist

A new directory or an updated directory ``web/dist`` should appear now with
HTML and javascript files that have been minified and "obfuscated" by ``gulp``.
For more details on the web interface, please refer to the dedicated chapter.

If everything has gone well, you should have installed the python application
on your system. The next step is to configure it for your platform and to
install the other components it relies on.
