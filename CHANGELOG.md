1.3.0 (released 07/01/2016)
===========================

    * [all] new feature scheduler: probe selection is based on file mimetype (default)
    * [all] new feature scheduler: probe could output children files that could be analyzed too (default)
    * [frontend] new API version (v1.1 old API is still available)
    * [frontend] tag a file and search by tag
    * [frontend][fix] UTF8 support
    * [frontend] cli tools is now a standalone project named irma-cli
    * [probe] probes now register on brain with their category and their mimetype support (regexp)
    * [probe][tools] new Unarchiver probe

1.2.1 (released 09/07/2015)
===========================

    * [frontend] new API command line client (with deserialized object)
    * [frontend] db migration system (powered by alembic)
    * [frontend] minor UI improvements
    * [probe][metadata] new TriD probe
    * [probe][external] new ICAP probe (by vrasneur)

1.2.0 (released 14/04/2015)
===========================

    * [frontend] new API (with swagger documentation)
    * [probe][antivirus] add support for Windows Avs:
        + avira, emsisoft
    * [probe][antivirus] add support for Linux Avs:
        + avast, avg, bitdefender,
        drweb, escan, fsecure,
        sophos, virusblokada, zoner
    * [probe][metadata] add support for PEiD
    * [frontend] minor UI addons (new json-explorer plugin)

1.1.1 (released 11/11/2014)
===========================

    * [frontend] add API documentation via swagger
    * [frontend] minor UI addons (sha1 in results page, cleaner scan progress page)
    * [frontend] fix problems when using pgsql
    * [probe] add support for GData/Yara probes

1.1.0 (released 07/10/2014)
===========================

    * [frontend] new summary view, new details view
    * [frontend] move from full NoSql to SQL+NoSql
    * remove Redis
    * [frontend] Sample stored on FS instead of NoSql (GridFS)
    * [frontend] move to vagrant/ansible install
    * [frontend] basic search (hash value, name)

1.0.4 (released 28/08/2014)
===========================

    * [frontend] results are splitted into a summary view and a details view
    * [frontend] formatters are now plugins
    * setup on single machine allowed
    * deb packaging with config dialogs
    * sphinx formatted docs (hosted on readthedocs.org)
    * better errors handling

1.0.3 (released 27/06/2014)
===========================

    * [frontend] add probe output filtering (called formatters)

1.0.2 (released 02/06/2014)
===========================

    * [frontend] new results display

1.0.1 (released 12/05/2014)
===========================

    * simple deb packaging

1.0   (released 29/03/2014)
===========================

    * First public release
    * pip packaging
    * [probe] support:
        * AV Linux:  Clamav,  Comodo, ESET, F-Prot, McAfee
        * AV Windows: Kaspersky, McAfee, Sophos, Symantec
        * NSRL
        * Virustotal API
        * PE static analyzer


