

=====================
Windows - Main Master
=====================

**requirements**

 * latest python 2.7 for windows `python27`_
 * pip package manager `pip_for_windows`_
 * install pip requirements-win.txt (see `install.rst`_)
 * install irma-probe-win package with pip (see `install.rst`_)

irma-probe-win package contains a batch file celery.bat, that could normally be found in default python scripts path ([PYTHON INSTALLDIR]\Scripts default is c:\Python27\Scripts).

**update boot script parameters**

This batch file update irma code and launch celery. Edit the parameters according to your installation:

.. code-block:: bash

    SET WORKDIR=c:\irma
    SET PIP_PKG=irma-probe-win
    SET LOCAL_PYPI_URL=http://brain.irma.qb:8000/pypi

**create a scheduled tasks**

Open Task scheduler

.. image:: images/scheduled1.png
   :alt: scheduled tasks
   :align: center

Choose a name, check:
    * execute even if user is not looged in
    * with maximum rights

.. image:: images/scheduled2.png
   :alt: scheduled tasks
   :align: center
   
setup action:
    * start a program: celery.bat
   
.. image:: images/scheduled3.png
   :alt: scheduled action
   :align: center
   
remove
    * stop task if runned for X days

.. image:: images/scheduled4.png
   :alt: scheduled tasks
   :align: center
   
halt your virtual machine, congratulations you are done with main windows7 master.

==========================
Windows - Antivirus Master
==========================

clone main windows 7 master with full copy of disk.
Rename your machine into 'master-<Antivirus_name>' (prefix is important)
install antivirus
if you choose the default install path nothing left to do.
if not you should add the custom install path to the PATH environment variable

.. image:: images/path1.png
   :alt: path
   :align: center

add your path with ';' delimiter

.. image:: images/path2.png
   :alt: path
   :align: center


.. _pip_for_windows https://sites.google.com/site/pydatalog/python/pip-for-windows
.. _python27 https://www.python.org/downloads/windows/
.. install.rst /install/install.rst
