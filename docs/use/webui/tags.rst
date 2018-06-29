Playing with tags
-----------------

.. note::

    Tags are available in IRMA from version 1.3.0

Creating a tag
^^^^^^^^^^^^^^

You could create tags by using the `command line tools <https://github.com/quarkslab/irma-cli>`_

.. code-block:: pycon

    >>> from irmacl.helpers import *
    >>> tag_list()
    []

    >>> tag_new("archive")
    {u'text': u'archive', u'id': 1}

    >>> tag_list()
    [Tag archive [1]]:

or directly from  your terminal by using curl and posting a json with 'text' key:

.. code-block:: console

    $ curl -H "Content-Type: application/json; charset=UTF-8"  -X POST -d '{"text":"<your tag>"}' http://172.16.1.30/api/v1.1/tags

.. note::

    There is currently no way to create a tag directly from the web IHM.


Tagging a File
^^^^^^^^^^^^^^

Directly in web IHM, once you are on a file details page:

.. image:: pics/add_tag1.png
   :alt: Add a tag to a file

Just click the tag bar and you will see all available tags. You could add multiple tags.

.. image:: pics/add_tag2.png
   :alt: See added tags

It is also possible to add a tag through command line tools:

.. code-block:: pycon

    >>> from irmacl.helpers import *
    >>> help(file_tag_add)
    Signature: file_tag_add(sha256, tagid, verbose=False)
    Docstring:
    Add a tag to a File

    :param sha256: file sha256 hash
    :type sha256: str of (64 chars)
    :param tagid: tag id
    :type tagid: int
    :return: No return

    >>> file_tag_add("346ae869f7c7ac7394196de44ab4cfcde0d1345048457d03106c1a0481fba853",1)

Searching by tag
^^^^^^^^^^^^^^^^

You could specify one or more tags while searching for files too:

.. image:: pics/search_tag1.png
   :alt: Add a tag while searching files

choose your tag list then hit the search button:

.. image:: pics/search_tag2.png
   :alt: Search by tag

or by command line:

.. code-block:: pycon

    >>> from irmacl.helpers import *
    >>> file_search(tags=[1])
    (1, [<irma.apiclient.IrmaResults at 0x7f079ca23890>])
