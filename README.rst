==========================================
IRMA: Incident Response & Malware Analysis
==========================================

|docs|

This is the main repository for IRMA, an asynchronous & customizable analysis
system for suspicious files.

This contain the documentation for IRMA project, which is built using
`Sphinx <http://sphinx-doc.org>`_ and is available online on the
`Read the Docs <https://readthedocs.org>`_ platform: |docs|.


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
    :target: https://readthedocs.org/projects/irma/
