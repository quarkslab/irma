Adding a new probe
------------------
Writing a Plugin for the probe
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::

 To be a valid probe module, IRMA expects it to have a predefined structure. To save time, one can get a minimal working structure from the skeleton plugin. The new plugin is stored in the appropriate sub-directory of the directory probe/modules according to the type of the new probe (antivirus, metadata, external...).

For a probe that is not a antivirus
***********************************
1. Copy the  directory skeleton to the new module (appropriate localisation).
Example with a module my_module with metadata type :

.. code-block:: console

    $ cp -r probe/modules/custom/skeleton/ probe/modules/metadata/my_module

2. If there are packages to install, specify them in the file requirements.txt. Otherwise remove the file
3. Adjust the file plugin.py according to the module :

  * Adjust the class's name with the name of your probe
  * Fill in the fields of the class :- _plugin_name_ = [the plugin name]

    - _plugin_display_name_ = [the field _name of the class of the probe]
    - _plugin_version_ = [the version number]
    - _plugin_category = [the type of the probe: IrmaProbeType.]
    - _plugin_description = [uick description]
    - _plugin_dependencies = [list of dependencies: platform, binary or/and file] => if used import from lib.plugins PlatformDependency, BinaryDependency or/and FileDependency
    - _mimetype_regexp = [mimetype corresponding]

4. Implement the functions corresponding to the type of the plugin

For an antivirus
****************
In the case of an antivirus, it is a little different because an Antivirus class was created to avoid code's duplication.
You can use the skeleton below:

plugin.py:

.. literalinclude:: plugin.py

The metaclass ``PluginMetaClass`` handles the registering of the plugin to a plugin manager. It also checks that the class is instanciable thanks to the ``verify`` method.

skeleton.py:

.. literalinclude:: skeleton.py


The recipe is the same, the files with the corresponding module name and differents fields need to be updated.
The attributes in ``Antivirus._attributes`` are meant to be defined by the instanciation. One can either:

  - leave it blank, in this case the super class will assign it a default value (eg. ``"unavailable"`` for ``self.version``);
  - define it directly (eg. ``self.scan_path = Path("/opt/skeleton/skeleton")``);
  - define a function to be called to assign it (eg. ``def get_scan_path(self): ...``), the super class will take care of calling it and handling exceptions.

Testing the new plugin
^^^^^^^^^^^^^^^^^^^^^^
Before testing, module's necessary stuff (binaries, files, etc) must be provisioned to the VM.

.. code-block:: console

    $ cd ansible
    $ vagrant rsync
    $ vagrant ssh
    $ sudo su deploy
    $ cd /opt/irma/irma-probe/current
    $ venv/bin/python -m extras.tools.run_module

This last command lists available modules.

Now, if the new module is available, its launching can be done:

.. code-block:: console

    $ venv/bin/python -m extras.tools.run_module my_module file

Automatic provisioning
^^^^^^^^^^^^^^^^^^^^^^^
Creating a new role
*******************
Create a new directory with this structure:

.. code-block:: console

   cd ansible
   tree roles/quarsklab.my_module
   roles/quarkslab.my_module/
   +-- defaults
   |   +-- main.yml
   +-- tasks
       +-- main.yml

tasks/main.yml is the default entry point for a role containing Ansible tasks.
In this file, write the instruction to install the module.
Add the file tasks/update.yml to write the informations for the update if necessary.
In defaults/main.yml it is usual to store default variables for this role.
If there are particular instructions, for example how to obtain a licence for a antivirus, add a README file.


Invoking the module role
*************************
Modify playbooks/provisioning.yml : add the module

.. code-block:: yaml

  -name : my_module
   hosts: my_module
   roles:
   - { role: quarkslab.my_module, tags: 'my_module'}

If a task update was defined, add the module in playbooks/updating.yml :

.. code-block:: yaml

  -name : my_module
   hosts: my_module
   roles:
   - { role: quarkslab.module, tags: 'my_module', task_from : update}


Defining hosts
**************

Modify the environment to add the new probe.

For example for the allinone_dev :

.. code-block :: console

 $ cat environments/allinone_dev.yml
 [ ... snip ... ]
     virustotal:
       - brain.irma
     my_module:
       - brain.irma
     "probe:children":
       - clamav
       - comodo
       - mcafee
       - static-analyzer
       - virustotal
       - my_module
