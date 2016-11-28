Probe
=====

The **Probes** are python-based application that host a single or multiple
analyzers. Each analyzer listens on a specific work queue and waits for an
analysis to be scheduled by the **Brain** through Celery, an open source task
framework for Python.


.. toctree::
   overview.rst
   install.rst
   configuration.rst
   analyzers.rst
   checks.rst
   daemon.rst

..
   linux.rst
   windows.rst
