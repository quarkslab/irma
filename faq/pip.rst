Install a python package with ``pip``
`````````````````````````````````````

.. code-block:: bash
  
   $ pip install <package-name>


Update a python package with ``pip``
````````````````````````````````````

.. code-block:: bash

   $ pip install --upgrade <package-name>


Install a specific version of a python package with ``pip``
```````````````````````````````````````````````````````````

.. code-block:: bash

   $ pip install <package-name>==<version>


Install all requirements with ``pip``
`````````````````````````````````````

.. code-block:: bash

   $ pip install -r requirements.txt


Install a custom python package with custom install path (e.g., IRMA packages)
``````````````````````````````````````````````````````````````````````````````

.. code-block:: bash

   $ pip install <package-name.tar.gz> --install-option='--install-base=<custom path>'

