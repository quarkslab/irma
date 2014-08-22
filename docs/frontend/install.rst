Installation
------------

The **Frontend** must be installed on a GNU/Linux system. With some efforts, it
should be possible to run it on a Microsoft Windows system, but this has not
been tested yet.

Through Packages
````````````````

Currently, a quick install through package is supported for Debian
Stable distributions. For other distributions or systems, please refer to
:ref:`install-source`.

Debian Stable
*************

First, add Quarklab's Debian repository to your APT repositories:

1. Add Quarkslab public GPG key:

.. code-block:: bash

    $ wget -O - http://www.quarkslab.com/qb-apt-key.asc | sudo apt-key add  -

.. note:: Checking Package Authenticity

    You can check the fingerprint of the key before trusting it to install new
    packages. Here is the fingerprint of Quarkslab's GPG public key:

    .. code-block:: bash

        $ sudo apt-key fingerprint
        [...]
        pub   4096R/143E8417 2014-06-26 [expires: 2019-06-25]
              Key fingerprint = B5CA 3608 A8E7 4A67 10DC  9343 E197 7836 143E 8417
        uid                  Debian Quarkslab APT archive <apt@quarkslab.com>


2. Add Quarkslab's repository as source

* for *Debian Stable*:

.. code-block:: bash

    $ echo 'deb http://apt.quarkslab.com/pub/debian stable main' | sudo tee /etc/apt/sources.list.d/quarkslab.list

* for *Debian Unstable*:

.. code-block:: bash

    $ echo 'deb http://apt.quarkslab.com/pub/debian-unstable unstable main' | sudo tee /etc/apt/sources.list.d/quarkslab.list


3. Update your APT cache

.. code-block:: bash

    $ sudo apt-get update

Then, install the meta-package ``irma-frontend``. This meta-package installs and
configure the python application (``irma-frontend-app``) which include the celery
worker and the restful API, the web server nginx (``irma-frontend-nginx``) and
the uwsgi application server (``irma-frontend-uwsgi``) , mongdb, and some
optionnal dependencies (``irma-frontend-rsyslog`` and ``irma-frontend-logrotate``).
By default, the python application will be installed in ``/opt/irma/irma-frontend/``.

.. code-block:: bash

    $ sudo apt-get install irma-frontend

At this point, the python-based application for the **Frontend** is installed
with its default configuration. See :ref:`app-configuration` to adapt the
default configuration to your settings.

.. _install-source:

Installation from source
````````````````````````

This section describes how to get the source code of the application and to
install it.

Downloading the source code from `github.com <https://github.com/quarkslab/irma-frontend>`_
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

Building the source distribution
********************************

We provide a Makefile that helps to build the python source distribution. By
default, the source distribution will be available in the ``dist/`` directory.
The created archive will be used to install the application.

.. code-block:: bash

    $ make source
    $ ls dist/
    irma-frontend-app-1.0.4.tar.gz

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

On GNU/Linux system, we will assume that the code for the **Frontend** will be
installed in ``/opt/irma/irma-frontend`` directory.

.. code-block:: bash

    $ pip install --install-option="--install-base=/opt/irma/irma-frontend" irma-frontend-app-1.0.4.tar.gz
    [...]

Since the way we packaged the python application does not so support
automatic installation of dependencies, we need to install them manually:

.. code-block:: bash

    $ pip install -r /opt/irma/irma-frontend/requirements.txt
    [...]

If everything has gone well, you should have installed the python application
on your system. The next step is to configure it for your platform and to
install the other components it relies on.
