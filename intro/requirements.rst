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
Windows 7 and 8 hosts have been tested.

We can not give you any specific numbers. On one hand we managed to run the
whole IRMA platform on a single machine by hosting it with multiple systems
inside virtual machines: this setup gives fairly high throughput as long as
it has reasonable IO (ideally, SSDs), and a good amount of memory (our setup
was an i7 cpu with 16 GB ram on regular drives (at least 200 GB required),
on the other hand, a lighter version of the system with the three parts together
[#]_  was successfully installed on a single virtual machine (1 GB of Ram and
4 virtual processors).

For a large company, in theory, given a single high-memory machine, with 16+ cores,
and SSDs, you could run IRMA platform and bear the workload load with reasonable
response time.

.. rubric:: Footnotes

.. [#] Theorically, it should be possible, with some efforts, to make IRMA work
       on Microsoft Windows systems as most of the components used for the platform
       are known to work or to have equivalents on these systems.
.. [#] For instance, we managed to host several GNU/Linux anti-viruses on an
       unique probe by preventing it to launch daemons at startup. This is
       difficult for Microsoft systems on which it is not recommended to
       install multiple anti-viruses on a single host.
.. [#] with a limited set of probes
