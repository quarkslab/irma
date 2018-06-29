Installation
------------

The **Brain** must be installed on a GNU/Linux distribution. With some efforts,
it should be possible to run it on a Microsoft Windows system, but this has not
been tested yet.

This section describes how to get the source code of the application for the
**Brain** and to install it.

Pre-requisites
++++++++++++++

We assume that you have a command line interface on your system with
the following tools installed:

* python 3.4.x and newer
* python3-pip (see `Install pip <https://pip.pypa.io/en/latest/installing.html>`_
  for the recommended way to install pip package manager)

Furthermore, we assume that you have created an user ``irma`` that will be used
to run the python application.

.. note:: On GNU/Linux, one can create the user (and the group) ``irma`` with:

    .. code-block:: console

        $ sudo adduser --system --no-create-home --group irma


Installation on GNU/Linux
+++++++++++++++++++++++++

On GNU/Linux system, we will assume that the code for the **Brain** will be
installed in ``/opt/irma/irma-brain/current`` directory, which is the configured
default installation directory.

The source code is hosted on github.com. One can fetch an up-to-date version
with the following commands. Let us note that there is a common submodule named
``common`` that is a soft-link (``lib``), do not forget the ``dereference``
option of ``cp`` (``-L``):


.. code-block:: console

    # If src repository not already cloned
    $ git clone https://github.com/quarkslab/irma /opt/irma/src
    $ cp -rL /opt/irma/src/brain /opt/irma/irma-brain/current

We need few dependencies for future steps:

    $ sudo apt-get install python3-virtualenv python3-dev


then, we need to install python dependencies manually in a virtualenv :

.. code-block:: console

    $ virtualenv --system-site-packages /opt/irma/irma-brain/current/venv
    $ /opt/irma/irma-brain/current/venv/bin/pip install -r /opt/irma/irma-brain/current/requirements.txt
    [...]


If everything has gone well, you should have installed the python application
on your system. The next step is to install the other components it relies on
and finally to configure it for your platform.
