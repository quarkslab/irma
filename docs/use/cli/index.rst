Command Line Interface
======================

For a use of IRMA by command line, use the
`command line tools <https://github.com/quarkslab/irma-cli>`_

**This api client is only made for IRMA API version 1.1.**

Installation
````````````
.. code-block:: bash

   $ python setup.py install


Configuration file contains the API endpoint (full url) and some optional paramters (max number and
delay in second between retries)

.. code-block:: none

   [Server]
   api_endpoint=http://172.16.1.30/api/v1.1
   max_tries=3
   pause=1


and is searched in these locations in following order:

* current directory
* environment variable ("IRMA_CONF")
* user home directory
* global directory  ("/etc/irma")


Once you set up a working irma.conf settings file, you could run tests on your running IRMA server:

.. code-block:: bash

   $ python setup.py test


Pip Install
-----------

Install it directly with pip:

.. code-block:: bash

  $ pip install irmacl


Usage
-----

.. code-block:: python

   >>> from irmacl.helpers import *
   >>> probe_list()
   [u'StaticAnalyzer', u'Unarchive', u'VirusBlokAda', u'VirusTotal']

   >>>  tag_list()
   [Tag malware [1], Tag clean [2], Tag suspicious [3]]

   >>>  scan_files(["./irma/tests/samples/eicar.com"], force=True, blocking=True)
   Scanid: ca2e8af4-0f5b-4a55-a1b8-2b8dc9ead068
   Status: finished
   Options: Force [True] Mimetype [True] Resubmit [True]
   Probes finished: 2
   Probes Total: 2
   Date: 2015-11-24 15:43:03
   Results: [<irma.apiclient.IrmaResults object at 0x7f3f250df890>]

   >>> scan = _
   >>> print scan.results[0]
   Status: 1
   Probes finished: 2
   Probes Total: 2
   Scanid: ca2e8af4-0f5b-4a55-a1b8-2b8dc9ead068
   Scan Date: 2015-12-22 14:36:21
   Filename: eicar.com
   Filepath: ./irmacl/tests/samples
   ParentFile SHA256: None
   Resultid: 572f9418-ca3c-4fdf-bb35-50c11629a7e7
   FileInfo:
   None
   Results: None

   >>> print scan_proberesults("572f9418-ca3c-4fdf-bb35-50c11629a7e7")
   Status: 1
   Probes finished: 2
   Probes Total: 2
   Scanid: ca2e8af4-0f5b-4a55-a1b8-2b8dc9ead068
   Scan Date: 2015-12-22 14:36:21
   Filename: eicar.com
   Filepath: ./irmacl/tests/samples
   ParentFile SHA256: None
   Resultid: 572f9418-ca3c-4fdf-bb35-50c11629a7e7
   FileInfo:
   Size: 68
   Sha1: 3395856ce81f2b7382dee72602f798b642f14140
   Sha256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
   Md5: 44d88612fea8a8f36de82e1278abb02fs
   First Scan: 2015-11-24 14:54:12
   Last Scan: 2015-12-22 14:36:21
   Id: 3
   Mimetype: EICAR virus test files
   Tags: []

   Results: [<irmacl.apiclient.IrmaProbeResult object at 0x7f3f250b9dd0>, <irmacl.apiclient.IrmaProbeResult object at 0x7f3f250b9850>]

   >>> fr = _
   >>> print fr.probe_results[0]
   Status: 1
   Name: VirusBlokAda (Console Scanner)
   Category: antivirus
   Version: 3.12.26.4
   Duration: 1.91s
   Results: EICAR-Test-File


Searching for scans

.. code-block:: python

   >>> scan_list()
   (89, [Scanid: ef0b9466-3132-40b7-990a-415f08377f09
     Status: finished
     Options: Force [True] Mimetype [True] Resubmit [True]
     Probes finished: 1
     Probes Total: 1
     Date: 2015-11-24 15:04:27
   [...]


Searching for files

.. code-block:: python

   >>> file_search(name="ei")
   (1, [<irmacl.apiclient.IrmaResults at 0x7f3f250491d0>])

   >>> (total, res) = _
   >>> print res[0]
   Status: 1
   Probes finished: 1
   Probes Total: 1
   Scanid: 7ae6b759-b357-4680-8358-b134b564b1ca
   Filename: eicar.com
   [...]

   >>> file_search(hash="3395856ce81f2b7382dee72602f798b642f14140")
   (7,
    [<irmacl.apiclient.IrmaResults at 0x7f3f250b96d0>,
     <irmacl.apiclient.IrmaResults at 0x7f3f24fdc1d0>,
     <irmacl.apiclient.IrmaResults at 0x7f3f24fdca90>,
     <irmacl.apiclient.IrmaResults at 0x7f3f24fdcdd0>,
     <irmacl.apiclient.IrmaResults at 0x7f3f24fdc690>,
     <irmacl.apiclient.IrmaResults at 0x7f3f2504f390>,
     <irmacl.apiclient.IrmaResults at 0x7f3f24fea350>])

   >>> file_search(hash="3395856ce81f2b7382dee72602f798b642f14140", tags=[1,2])
   (0, [])

   # looking for an unexisting tagid raise IrmaError
   >>> file_search(hash="3395856ce81f2b7382dee72602f798b642f14140", tags=[100])
   IrmaError: Error 402


Objects (apiclient.py)
----------------------

**class irmacl.apiclient.IrmaFileInfo(id, size, timestamp_first_scan, timestamp_last_scan, sha1, sha256, md5, mimetype, tags)**

   Bases: "object"

   IrmaFileInfo Description for class

   Variables:
      * **id** -- id

      * **timestamp_first_scan** -- timestamp when file was first
        scanned in IRMA

      * **timestamp_last_scan** -- timestamp when file was last
        scanned in IRMA

      * **size** -- size in bytes

      * **md5** -- md5 hexdigest

      * **sha1** -- sha1 hexdigest

      * **sha256** -- sha256 hexdigest

      * **mimetype** -- mimetype (based on python magic)

      * **tags** -- list of tags

   pdate_first_scan -- property, humanized date of first scan

   pdate_last_scan -- property, humanized date of last scan

   raw()

**class irmacl.apiclient.IrmaProbeResult(**kwargs)**

   Bases: "object"

   IrmaProbeResult Description for class

   Variables:
      * **status** -- int probe specific (usually -1 is error, 0
        nothing found 1 something found)

      * **name** -- probe name

      * **type** -- one of IrmaProbeType ('antivirus', 'external',
        'database', 'metadata'...)

      * **version** -- probe version

      * **duration** -- analysis duration in seconds

      * **results** -- probe results (could be str, list, dict)

      * **error** -- error string (only relevant in error case when
        status == -1)

      * **external_url** -- remote url if available (only relevant
        when type == 'external')

      * **database** -- antivirus database digest (need unformatted
        results) (only relevant when type == 'antivirus')

      * **platform** -- 'linux' or 'windows' (need unformatted
        results)

   to_json()


**class irmacl.apiclient.IrmaResults(file_infos=None, probe_results=None, **kwargs)**

   Bases: "object"

   IrmaResults Description for class

   Variables:
      * **status** -- int (0 means clean 1 at least one AV report
        this file as a virus)

      * **probes_finished** -- number of finished probes analysis
        for current file

      * **probes_total** -- number of total probes analysis for
        current file

      * **scan_id** -- id of the scan

      * **scan_date** -- date of the scan

      * **name** -- file name

      * **path** -- file path (as sent during upload or resubmit)

      * **result_id** -- id of specific results for this file and
        this scan used to fetch probe_results through file_results
        helper function

      * **file_infos** -- IrmaFileInfo object

      * **probe_results** -- list of IrmaProbeResults objects

   to_json()

   pscan_date -- property, humanized date of scan date


**class irmacl.apiclient.IrmaScan(id, status, probes_finished, probes_total, date, force, resubmit_files, mimetype_filtering, results=[])**

   Bases: "object"

   IrmaScan Description for class

   Variables:
      * **id** -- id of the scan

      * **status** -- int (one of IrmaScanStatus)

      * **probes_finished** -- number of finished probes analysis
        for current scan

      * **probes_total** -- number of total probes analysis for
        current scan

      * **date** -- scan creation date

      * **force** -- force a new analysis or not

      * **resubmit_files** -- files generated by the probes should
        be analyzed or not

      * **mimetype_filtering** -- probes list should be decided
        based on files mimetype or not

      * **results** -- list of IrmaResults objects

   is_finished()

   is_launched()

   pdate  -- property, printable date

   pstatus -- property, printable status

**class irmacl.apiclient.IrmaTag(id, text)**

   Bases: "object"

   IrmaTag Description for class

   Variables:
      * **id** -- id of the tag

      * **text** -- tag label


Helpers (helpers.py)
--------------------

**irmacl.helpers.file_download(sha256, dest_filepath, verbose=False)**

   Download file identified by sha256 to dest_filepath

   Parameters:
      * **sha256** (*str of 64 chars*) -- file sha256 hash value

      * **dest_filepath** (*str*) -- destination path

      * **verbose** (*bool*) -- enable verbose requests (optional
        default:False)

   Returns:
      return tuple of total files and list of results for the given
      file

   Return type:
      tuple(int, list of IrmaResults)

**irmacl.helpers.file_results(sha256, limit=None, offset=None, verbose=False)**

   List all results for a given file identified by sha256

   Parameters:
      * **sha256** (*str of 64 chars*) -- file sha256 hash value

      * **limit** (*int*) -- max number of files to receive
        (optional default:25)

      * **offset** (*int*) -- index of first result (optional
        default:0)

      * **verbose** (*bool*) -- enable verbose requests (optional
        default:False)

   Returns:
      tuple(int, list of IrmaResults)

**irmacl.helpers.file_search(name=None, hash=None, tags=None, limit=None, offset=None, verbose=False)**

   Search a file by name or hash value

   Parameters:
      * **name** (*str*) -- name of the file ('*name*' will be
        searched)

      * **hash** (*str of (64, 40 or 32 chars)*) -- one of sha1, md5
        or sha256 full hash value

      * **tags** (*list of int*) -- list of tagid

      * **limit** (*int*) -- max number of files to receive
        (optional default:25)

      * **offset** (*int*) -- index of first result (optional
        default:0)

      * **verbose** (*bool*) -- enable verbose requests (optional
        default:False)

   Returns:
      return tuple of total files and list of matching files already
      scanned

   Return type:
      tuple(int, list of IrmaResults)

**irmacl.helpers.file_tag_add(sha256, tagid, verbose=False)**

   Add a tag to a File

   Parameters:
      * **sha256** (*str of (64 chars)*) -- file sha256 hash

      * **tagid** (*int*) -- tag id

   Returns:
      No return

**irmacl.helpers.file_tag_remove(sha256, tagid, verbose=False)**

   Remove a tag to a File

   Parameters:
      * **sha256** (*str of (64 chars)*) -- file sha256 hash

      * **tagid** (*int*) -- tag id

   Returns:
      No return

**irmacl.helpers.probe_list(verbose=False)**

   List availables probes

   Parameters:
      **verbose** (*bool*) -- enable verbose requests (optional
      default:False)

   Returns:
      return probe list

   Return type:
      list

**irmacl.helpers.scan_add_data(scan_id, data, filename, post_max_size_M=100, verbose=False)**

   Add files to an existing scan

   Parameters:
      * **scan_id** (*str*) -- the scan id

      * **data** (*str*) -- data to scan

      * **filename** (*str*) -- filename associated to data

      * **post_max_size_M** (*int*) -- POST data max size in Mb (multiple calls to the
        api will be done if total size is more than this limit, note that if
        one or more file is bigger than this limit it will raise an error)

      * **verbose** (*bool*) -- enable verbose requests (optional
        default:False)

   Returns:
      return the updated scan object

   Return type:
      IrmaScan


**irmacl.helpers.scan_add_files(scan_id, filelist, post_max_size_M=100, verbose=False)**

   Add files to an existing scan

   Parameters:
      * **scan_id** (*str*) -- the scan id

      * **filelist** (*list*) -- list of full path qualified files

      * **post_max_size_M** (*int*) -- POST data max size in Mb (multiple calls to the
        api will be done if total size is more than this limit, note that if
        one or more file is bigger than this limit it will raise an error)

      * **verbose** (*bool*) -- enable verbose requests (optional
        default:False)

   Returns:
      return the updated scan object

   Return type:
      IrmaScan

**irmacl.helpers.scan_cancel(scan_id, verbose=False)**

   Cancel a scan

   Parameters:
      * **scan_id** (*str*) -- the scan id

      * **verbose** (*bool*) -- enable verbose requests (optional
        default:False)

   Returns:
      return the scan object

   Return type:
      IrmaScan

**irmacl.helpers.scan_data(data, filename, force, post_max_size_M=100, probe=None, mimetype_filtering=None, resubmit_files=None, blocking=False,blocking_timeout=60, verbose=False)**

   Wrapper around scan_new / scan_add / scan_launch

   Parameters:
      * **data** (*str*) -- data to scan

      * **filename** (*str*) -- filename associated to data

      * **force** (*bool*) -- if True force a new analysis of files
        if False use existing results

      * **post_max_size_M** (*int*) -- POST data max size in Mb (multiple calls to the
        api will be done if total size is more than this limit, note that if
        one or more file is bigger than this limit it will raise an error)

      * **probe** (*list*) -- probe list to use (optional default:
        None means all)

      * **mimetype_filtering** (*bool*) -- enable probe selection
        based on mimetype (optional default:True)

      * **resubmit_files** (*bool*) -- reanalyze files produced by
        probes (optional default:True)

      * **blocking** (*bool*) -- wether or not the function call
        should block until scan ended

      * **blocking_timeout** (*int*) -- maximum amount of time
        before timeout per file (only enabled while blocking is ON)

      * **verbose** (*bool*) -- enable verbose requests (optional
        default:False)

   Returns:
      return the scan object

   Return type:
      IrmaScan


**irmacl.helpers.scan_files(filelist, force, post_max_size_M=100, probe=None, mimetype_filtering=None, resubmit_files=None, blocking=False,blocking_timeout=60, verbose=False)**

   Wrapper around scan_new / scan_add / scan_launch

   Parameters:
      * **filelist** (*list*) -- list of full path qualified files

      * **force** (*bool*) -- if True force a new analysis of files
        if False use existing results

      * **post_max_size_M** (*int*) -- POST data max size in Mb (multiple calls to the
        api will be done if total size is more than this limit, note that if
        one or more file is bigger than this limit it will raise an error)

      * **probe** (*list*) -- probe list to use (optional default:
        None means all)

      * **mimetype_filtering** (*bool*) -- enable probe selection
        based on mimetype (optional default:True)

      * **resubmit_files** (*bool*) -- reanalyze files produced by
        probes (optional default:True)

      * **blocking** (*bool*) -- wether or not the function call
        should block until scan ended

      * **blocking_timeout** (*int*) -- maximum amount of time
        before timeout per file (only enabled while blocking is ON)

      * **verbose** (*bool*) -- enable verbose requests (optional
        default:False)

   Returns:
      return the scan object

   Return type:
      IrmaScan

**irmacl.helpers.scan_get(scan_id, verbose=False)**

   Fetch a scan (useful to track scan progress with scan.pstatus)

   Parameters:
      * **scan_id** (*str*) -- the scan id

      * **verbose** (*bool*) -- enable verbose requests (optional
        default:False)

   Returns:
      return the scan object

   Return type:
      IrmaScan

**irmacl.helpers.scan_launch(scan_id, force, probe=None, mimetype_filtering=None, resubmit_files=None, verbose=False)**

   Launch an existing scan

   Parameters:
      * **scan_id** (*str*) -- the scan id

      * **force** (*bool*) -- if True force a new analysis of files
        if False use existing results

      * **probe** (*list*) -- probe list to use (optional default
        None means all)

      * **mimetype_filtering** (*bool*) -- enable probe selection
        based on mimetype (optional default:True)

      * **resubmit_files** (*bool*) -- reanalyze files produced by
        probes (optional default:True)

      * **verbose** (*bool*) -- enable verbose requests (optional
        default:False)

   Returns:
      return the updated scan object

   Return type:
      IrmaScan

**irmacl.helpers.scan_list(limit=None, offset=None, verbose=False)**

   List all scans

   Parameters:
      * **limit** (*int*) -- max number of files to receive
        (optional default:25)

      * **offset** (*int*) -- index of first result (optional
        default:0)

      * **verbose** (*bool*) -- enable verbose requests (optional
        default:False)

   Returns:
      return tuple of total scans and list of scans

   Return type:
      tuple(int, list of IrmaScan)

**irmacl.helpers.scan_new(verbose=False)**

   Create a new scan

   Parameters:
      **verbose** (*bool*) -- enable verbose requests (optional
      default:False)

   Returns:
      return the new generated scan object

   Return type:
      IrmaScan

**irmacl.helpers.scan_proberesults(result_idx, formatted=True, verbose=False)**

   Fetch file probe results (for a given scan
      one scan <-> one result_idx

   Parameters:
      * **result_idx** (*str*) -- the result id

      * **formatted** (*bool*) -- apply frontend formatters on
        results (optional default:True)

      * **verbose** (*bool*) -- enable verbose requests (optional
        default:False)

   Returns:
      return a IrmaResult object

   Return type:
      IrmaResults

**irmacl.helpers.tag_list(verbose=False)**

   List all available tags

   Returns:
      list of existing tags

   Return type:
      list of IrmaTag

**irmacl.helpers.tag_new(text, verbose=False)**

   Create a new tag

   Parameters:
      **text** (*str*) -- tag label (utf8 encoded)

   Returns:
      None
