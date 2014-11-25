Supported Analyzers
-------------------

We have mainly focused our efforts on multiple anti-virus engines but we are
working on other kind of "probes". We enumerate the analyzers that are bundled
with IRMA probe application. Feel free to submit your own probes.

Antiviruses
```````````

So far, we have instrumented the following antiviruses from their CLI:


========== ============================== =========================================== ============================= =======
Probe Name Anti-Virus Name                Description                                 Platform                      CLI/GUI
========== ============================== =========================================== ============================= =======
ClamAV     ClamAV                         Instruments ClamAV Daemon                   GNU/Linux                     CLI
ComodoCAVL Comodo Antivirus for Linux     Instruments Comodo Free Antivirus for Linux GNU/Linux                     CLI
EsetNod32  Eset Nod32 Business Edition    Instruments Eset Nod32 Business Edition     GNU/Linux                     CLI
FProt      F-Prot                         Instruments F-Prot Antivirus                GNU/Linux                     CLI
McAfeeVSCL McAfee VirusScan Command Line  Instruments McAfee                          GNU/Linux - Microsoft Windows CLI
Sophos     Sophos                         Instruments Sophos                          Microsoft Windows             CLI
Kaspersky  Kaspersky Internet Security    Instruments Kaspersky Internet Security     Microsoft Windows             CLI
Symantec   Symantec Endpoint Protection   Instruments Symantec Endpoint Protection    Microsoft Windows             CLI
GData      G Data Antivirus               Instruments G Data Antivirus                Microsoft Windows             CLI
========== ============================== =========================================== ============================= =======


External analysis platforms
```````````````````````````

So far, we query the following external analysis platforms:

========== ================= =================================================================
Probe Name Analysis Platform Description
========== ================= =================================================================
VirusTotal VirusTotal        Report is searched using the sha256 of the file which is not sent
========== ================= =================================================================


File database
`````````````

So far, we query the following file databases:

========== =================================== ==========================================================================
Probe Name Database                            Description
========== =================================== ==========================================================================
NSRL       National Software Reference Library collection of digital signatures of known, traceable software applications
========== =================================== ==========================================================================

Binary analyzers
````````````````

So far, we implemented the following binary analyzers:

============== ================ ============================================
Probe Name     Analyzer         Description
============== ================ ============================================
StaticAnalyzer PE File Analyzer PE File analyzer adapted from Cuckoo Sandbox
============== ================ ============================================

Others
``````

Additionnally, the following modules are available:

============== ============================================
Probe Name     Description
============== ============================================
Yara           Checks if a file match yara rules
============== ============================================


