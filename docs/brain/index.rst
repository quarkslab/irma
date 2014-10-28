Brain - Manual Install
======================

The **Brain** is a python-based application that only dispatches analysis
requests from different frontends [#]_ to the available **Probes**. Analyses
are scheduled by the **Brain** on **Probes** through Celery, an open source
task framework for Python.

.. toctree::

   overview.rst
   rabbitmq.rst
   ftpd.rst
   install.rst
   configuration.rst
   checks.rst
   daemon.rst

.. rubric:: Footnotes

.. [#] This feature is not ready yet, we are currently working on its
       implementation.
