Supported Analyzers
-------------------

Here is the list of analyzers that are bundled with IRMA.

Antiviruses
```````````

====================== ============================== =================================
Probe Name             Anti-Virus Name                Platform
====================== ============================== =================================
ASquaredCmdWin         Emsisoft Command Line          Microsoft Windows             CLI
AvastCoreSecurity      Avast Core Security            GNU/Linux                     CLI
AVGAntiVirusFree       AVG                            GNU/Linux                     CLI
AviraWin               Avira                          Microsoft Windows             CLI
BitdefenderForUnices   Bitdefender                    GNU/Linux                     CLI
ClamAV                 ClamAV                         GNU/Linux                     CLI
ComodoCAVL             Comodo Antivirus for Linux     GNU/Linux                     CLI
DrWeb                  Dr.Web                         GNU/Linux                     CLI
EScan                  eScan                          GNU/Linux                     CLI
EsetFileSecurity       Eset File Security             GNU/Linux                     CLI
FProt                  F-Prot                         GNU/Linux                     CLI
FSecure                F-Secure                       GNU/Linux                     CLI
GDataWin               G Data Antivirus               Microsoft Windows             CLI
Kaspersky              Kaspersky File Server          GNU/Linux                     CLI
KasperskyWin           Kaspersky Internet Security    Microsoft Windows             CLI
McAfeeVSCL             McAfee VirusScan Command Line  GNU/Linux                     CLI
McAfeeVSCLWin          McAfee VirusScan Command Line  Microsoft Windows             CLI
Sophos                 Sophos                         GNU/Linux                     CLI
SophosWin              Sophos Endpoint Protection     Microsoft Windows             CLI
SymantecWin            Symantec Endpoint Protection   Microsoft Windows             CLI
VirusBlokAda           VirusBlokAda                   GNU/Linux                     CLI
Zoner                  Zoner Antivirus                GNU/Linux                     CLI
====================== ============================== =================================


External analysis platforms
```````````````````````````

========== ================= =================================================================
Probe Name Analysis Platform Description
========== ================= =================================================================
ICAP       ICAP              Query an ICAP server
VirusTotal VirusTotal        Report is searched using the sha256 of the file which is not sent
========== ================= =================================================================


File database
`````````````

========== =================================== ==========================================================================
Probe Name Database                            Description
========== =================================== ==========================================================================
NSRL       National Software Reference Library collection of digital signatures of known, traceable software applications
========== =================================== ==========================================================================

Metadata
````````

============== ============================================
Probe Name     Description
============== ============================================
LIEF           PE/ELF File analyzer
PEiD           PE File packer analyzer
TrID           File type identification
StaticAnalyzer PE File analyzer adapted from Cuckoo Sandbox
Yara           Checks if a file match yara rules
============== ============================================
