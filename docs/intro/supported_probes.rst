Supported Analyzers
-------------------

We have mainly focused our efforts on multiple anti-virus engines but we are
working on other kind of "probes". We enumerate the analyzers that are bundled
with IRMA probe application. Feel free to submit your own probes.

Antiviruses
```````````

So far, we have instrumented the following antiviruses from their CLI:


====================== ============================== =================================
Probe Name             Anti-Virus Name                Platform
====================== ============================== =================================
ASquaredCmd            Emsisoft Command Line          Microsoft Windows             CLI
Avira                  Avira                          Microsoft Windows             CLI
AvastCoreSecurity      Avast                          GNU/Linux                     CLI
AVGAntiVirusFree       AVG                            GNU/Linux                     CLI
BitdefenderForUnices   Bitdefender                    GNU/Linux                     CLI
ClamAV                 ClamAV                         GNU/Linux                     CLI
ComodoCAVL             Comodo Antivirus for Linux     GNU/Linux                     CLI
DrWeb                  Dr.Web                         GNU/Linux                     CLI
EsetNod32              Eset Nod32 Business Edition    GNU/Linux                     CLI
EScan                  eScan                          GNU/Linux                     CLI
FProt                  F-Prot                         GNU/Linux                     CLI
FSecure                F-Secure                       GNU/Linux                     CLI
GData                  G Data Antivirus               Microsoft Windows             CLI
Kaspersky              Kaspersky Internet Security    Microsoft Windows             CLI
McAfeeVSCL             McAfee VirusScan Command Line  GNU/Linux - Microsoft Windows CLI
Sophos                 Sophos                         GNU/Linux - Microsoft Windows CLI
Symantec               Symantec Endpoint Protection   Microsoft Windows             CLI
VirusBlokAda           VirusBlokAda                   GNU/Linux                     CLI
Zoner                  Zoner Antivirus                GNU/Linux                     CLI
====================== ============================== =================================


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

Metadata
````````

So far, we implemented the following analyzers:

============== ============================================
Probe Name     Description
============== ============================================
StaticAnalyzer PE File analyzer adapted from Cuckoo Sandbox
PEiD		   PE File packer analyzer
Yara           Checks if a file match yara rules
============== ============================================
