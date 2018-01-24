2.0.4 (released 22/12/2017)
===========================

    * Bugfixes


2.0.3 (released 15/12/2017)
===========================

    * [frontend] fix file cleanup

2.0.2 (released 21/11/2017)
===========================

    * [frontend] PKI updated support client cert
    * [frontend] allow standalone SQL server (new ansible host sql-server to add)
    * [frontend/api] Add /about endpoint to display version
    * [probe] Add DrWeb file server linux AV

2.0.1 (released 17/10/2017)
===========================

    * [all] Virus DB version is supported and displayed when available
    * [frontend/api] add a list of results for a file to quickly jump to other results
    * [frontend] Delete file according to a max size settings (could be combined with max days)
    * [all] Update default box to debian9
    * [all] Use random diskname for libvirt
    * [brain/probe] retry on rabbitmq down
    * [probe] Add kaspersky linux and Eset file server linux AVs

2.0.0 (released 08/09/2017)
===========================

    * [frontend] API/V2 WIP (not stable version yet)
    * [all] Move to python3
    * [frontend] Move to hug
    * [frontend] scan load optimization
    * [frontend] enable CORS by default
    * [probe] bugfixes

1.5.3 (released 28/11/2016)
===========================

    * [all] New organization for repositories (all repos are merged in one irma repo now)
    * [frontend] scan load optimization

1.5.2 (released 14/10/2016)
===========================

    * [all] Allow sftp authentication by key
    * [frontend] SQL allow file over 2 GB
    * [all] bugfix for job cancelling

1.5.1 (released 07/06/2016)
===========================

    * [brain] code refactor: celery daemons splitted in two distinct files
    * [brain] more unittests
    * [frontend] Fix: using cache results was not done in some cases

1.5.0 (released 28/05/2016)
===========================

    * [frontend] Storing probe results in PostgreSQL instead of MongoDB.
            This will break all upgrades attempts but will
            make easier the process of having data stored outside of IRMA.
    * [all] Probe now have a display name
    * [all] bugfix job error handling and job cancel

1.4.2 (released 23/05/2016)
===========================

    * [frontend] Fix: resubmition of previously deleted file.


1.4.1 (released 12/05/2016)
===========================

    * [frontend] bugfix: Unarchiver file resubmition fixed


1.4.0 (released 03/05/2016)
===========================

    * [all] Default transport mode switch from ftp/tls to sftp
    * [all] Better handling of large files
    * [all] Support Rabbitmq SSL
    * [frontend] File search now ordered by name
    * [frontend] File search now returns the latest analysis

1.3.2  (released 10/03/2016)
============================

    * [all] add a debug option for log
    * [brain] bugfix (probelist issue, sometimes returning an empty list)

1.3.1 (released 01/03/2016)
===========================

    * [brain] bugfix (probe offline was not detected)
    * [frontend] bugfix (fast scan, in some cases, was running forever)

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


