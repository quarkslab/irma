******************************
Web Interface - Manual Install
******************************

============
Installation
============

Here are the few steps needed to get the interface up and running

**1. Make sure you have node installed**

Node is needed to fetch the dependencies (``npm`` for the server side,
``bower`` for the client side), and to launch the task runner (``gulp``). You
can get it from many ways, choose the one that suits you better on their
website:  `nodeJs`_.


**2. Install the development tools**

Those two work better when installed globally, you may need root privileges to install them this way

.. code-block:: bash

    $ npm install -g bower gulp

**3. Fetch the dependencies**

The rest of the dependencies can then be fetched with this command:

.. code-block:: bash

    $ npm install

If everything went fine, ``bower`` and the ``webdriver-manager`` should launch
their respective updates right after ``npm install`` is done.  If not, here
they are:

.. code-block:: bash

    $ bower install
    $ webdriver-manager update

======
Usage
======

-----
Tests
-----

There are 3 steps that can check code integrity:

**Linting**

.. code-block:: bash

    $ gulp lint

**Unit tests**

.. code-block:: bash

    $ gulp unit

**End to end tests**

These tests need to access the interface through a web server, so you will have to launch one.
There is a standalone server embeded in the project, just launch it in another shell with:

.. code-block:: bash

    # in another shell
    $ npm start

The end to end tests can then be checked with another gulp task:

.. code-block:: bash

    $ gulp e2e

------------------

You can launch those 3 in sequence with the ``full`` task. You will need the standalone server running for the E2E tests.

.. code-block:: bash

    $ gulp full


-----
Build
-----

To get a bundled and production ready version of the interface, use the ``dist`` task, which will build a ``dist`` directory.

.. code-block:: bash

    $ gulp dist


------------

.. _nodeJs: http://nodejs.org/
