File Analysis Process
=====================

#. An analysis begins when a user uploads files to the **Frontend**.
#. **Frontend** checks for existing files and results in mongodb. If needed,
   it stores the new files and calls asynchronously scan jobs on **Brain**.
#. **Brain** worker sends as much subtasks to **Probe(s)** as needed.
#. **Probe** workers process their jobs and send back results to **Brain**.
#. **Brain** sends results to **Frontend**.

.. image:: ../images/irma/overview.jpg
   :alt: Analysis workflow
