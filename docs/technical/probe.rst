Probe
=====

The **Probes** are python-based application that host a single or multiple analyzers. Each analyzer listens on a specific work queue and waits for an analysis to be scheduled by the **Brain** through Celery, an open source task framework for Python.
Python version should be at least 3.4 on linux, 3.5 on windows.

Architecture
------------

**Probes** are mainly Celery workers that handle scan requests from **Brain**
