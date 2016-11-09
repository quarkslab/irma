Brain
=====

The **Brain** is a python-based application that only dispatches analysis
requests from different frontends [#]_ to the available **Probes**. Analyses
are scheduled by the **Brain** on **Probes** through Celery, an open source
task framework for Python.

.. toctree::

   overview.rst
   rabbitmq.rst
   sftp.rst
   install.rst
   configuration.rst
   checks.rst
   supervisor.rst

.. rubric:: Footnotes

.. [#] This feature is not ready yet, we are currently working on its
       implementation.
