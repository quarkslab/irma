==========================================
IRMA: Incident Response & Malware Analysis
==========================================

|docs|

This is the main repository for IRMA, an asynchronous & customizable analysis
system for suspicious files.

This contain the documentation for IRMA project, which is built using
`Sphinx <http://sphinx-doc.org>`_ and is available online on the
`Read the Docs <https://readthedocs.org>`_ platform.


Repositories
============

If you want to try/install IRMA, read the doc that will
guide you to automatic install process. All scripts are
hosted at our vagrant/ansible repository:

* `Ansible <https://github.com/quarkslab/irma-ansible>`_

If you want to take a look at the sources or go through
the manual install process:

* `Frontend <https://github.com/quarkslab/irma-frontend>`_
* `Brain <https://github.com/quarkslab/irma-brain>`_
* `Probe <https://github.com/quarkslab/irma-probe>`_

all got a common dependency named irma-common that is set as a submodule in all three repositories:

* `Common <https://github.com/quarkslab/irma-common>`_


Resources
=========

* `Project website <http://irma.quarkslab.com>`_
* `IRC <irc://irc.freenode.net/qb_irma>`_  (irc.freenode.net, #qb_irma)
* `Twitter <https://twitter.com/qb_irma>`_ (@qb_irma)


Build the documentation
=======================

You'll need to install `Sphinx <http://sphinx-doc.org>`_, and the run:

.. code-block:: bash

    $ make # to see all build options available
    $ make html

Open your browser to the ``_build/html/index.html`` file.


.. |docs| image:: https://readthedocs.org/projects/irma/badge/
    :alt: Documentation Status
    :scale: 100%
    :target: https://irma.readthedocs.org/
