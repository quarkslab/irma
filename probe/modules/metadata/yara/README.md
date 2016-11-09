irma-probe-yara
===============

  Yara Module for IRMA

  Bryan Nolen @BryanNolen

#To install:#

1. Install Yara or Greater, and its associated yara-python module (be mindful of the python virtualenv that the probes run in)

2. Modify the config.ini file to represent the location where you are storing your yara rules file.
  (By default this will look for it at `/opt/irma/yara_rules/yara_rules.yar`)

3. Test the module:
  ```
  cd /opt/irma/irma-probe/current
  venv/bin/python -m tools.run_module Yara /bin/bash
  ```

4. Restart the probe_app
  ```
  sudo supervisorctl restart probe_app
  ```

5. Verify that the Yara module is present on the web interface under advanced options.
