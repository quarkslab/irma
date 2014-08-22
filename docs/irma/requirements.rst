Hardware requirements
=====================

IRMA platform is divided in three major components: the **Frontend**, the
**Brain** and one or multiple **Probes**. 

These three components can be installed on a unique host or on multiple hosts,
according to the kind of probes you are using. 

The **Frontend** and the **Brain** must be installed on a GNU/Linux
system [#]_. We recommend to use a Debian Stable distribution which is
supported and known to work.

According to the kind of probes and their dependencies, each analyzers can be
installed on a separate hosts or share the same host as far as they do not
interfere with each other [#]_. So forth, only Debian Stable and Microsoft
Windows 7 hosts have been tested.

We do not have any real numbers to tell you what kind of hardware you are going
to need. We managed to run off the whole IRMA platform a single machine [#]_ by
hosting with multiple systems inside virtual machines. 


This setup gives fairly high throughput as long as it has reasonable IO
(ideally, SSDs), and a good amount of memory. For a large company, in theory,
given a single high-memory machine, with 16+ cores, and SSDs, you could run
IRMA platform and bear the workload load with reasonnable response time.

.. rubric:: Footnotes

.. [#] Theorically, it should be possible, with some efforts, to make IRMA work
       on Microsoft Windows systems as most of the components used for the platform
       are known to work or to have equivalents on these systems.
.. [#] For instance, we managed to host several GNU/Linux anti-viruses on an
       unique probe by preventing it to launch daemons at startup. This is
       difficult for Microsoft systems on which it is not recommended to
       install multiple anti-viruses on a single host.
.. [#] For the proof-of-concept, we even managed to run the whole platform,
       with a limited set of probes, on a single virtual machine.
