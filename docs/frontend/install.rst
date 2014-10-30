Installation
------------

Currently, a quick install through vagrant and ansible scripts is supported.
It is the recommended way to proceed but if you want to go more into the details,
here is the manual install guide.


The **Frontend** must be installed on a GNU/Linux system. With some efforts, it
should be possible to run it on a Microsoft Windows system, but this has not
been tested yet.

This section describes how to get the source code of the application and to
install it.

Downloading the source code from github
*******************************************************************************************

The source code is hosted on github.com. One can fetch an up-to-date version
with the following commands. Let us note that there is a common submodule named
``irma-common`` that could be fetched automatically with the ``--recursive``
option:

.. code-block:: bash

    $ git clone --recursive https://github.com/quarkslab/irma-frontend

Building the web client
***********************

The first step that should be performed when installing the frontend from the
code source is to build the web client which is composed of static HTML files
mixed with javascript web framework (in particular, AngularJS).

One must install first some tools that are necessary to build the whole web
client. At the time of writing, Node.js is available in the default Debian
Wheezy repositories (if not, add ``wheezy-backports`` repository):

.. code-block:: bash

    $ echo "deb http://ftp.fr.debian.org/debian/ wheezy-backports main contrib non-free" | sudo tee /etc/apt/source.list.d/wheezy-backports.list
    [...]
    $ sudo apt-get install nodejs
    [...]
    $ curl https://www.npmjs.org/install.sh | sudo sh
    [...]

Once the tools installed, you can build the static files for the web user
interface with the following commands, executed from the installation
directory:

.. code-block:: bash

    $ cd web
    $ npm install
    $ node_modules/.bin/bower install
    $ node_modules/.bin/gulp dist

A new directory or an updated directory ``web/dist`` should appear now with
HTML and javascript files that have been minified and "obfuscated" by ``gulp``.
For more details on the web interface, please refer to the dedicated chapter.

Building the source distribution
********************************

We provide a ``Makefile`` that helps to build the python source distribution.
By default, the source distribution will be available in the ``dist/``
directory.  The created archive will be used to install the application.

.. code-block:: bash

    $ make source
    $ ls dist/
    irma-frontend-app-1.1.0.tar.gz

.. note:: Required tools to build the source distribution

    Few tools are needed to build the python source distribution and to install
    the application:

    * make
    * python-pip
    * python-setuptools

Installing the source distribution
**********************************

To be able to install the python source distribution, we assume that you have
already install the following software on your system. The prerequisites are
recalled here.

Prerequisites
+++++++++++++

We assume that you have a command line interface on your system with
the following tools installed:

* python 2.7.x
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
installed in ``/opt/irma/irma-frontend`` directory.

.. code-block:: bash

    $ pip install --install-option="--install-base=/opt/irma/irma-frontend" irma-frontend-app-1.1.0.tar.gz
    [...]

Since the way we packaged the python application does not support
automatic installation of dependencies, we need to install them manually:

.. code-block:: bash

    $ pip install -r /opt/irma/irma-frontend/requirements.txt
    [...]

If everything has gone well, you should have installed the python application
on your system. The next step is to configure it for your platform and to
install the other components it relies on.
