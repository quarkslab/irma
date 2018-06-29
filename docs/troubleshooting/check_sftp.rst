Check SFTP accounts
===================

Try to login as ``frontend`` and upload a sample file in home dir (should raise an error as
it is non writeable) then in ``uploads`` dir.

.. code-block:: console

    $ sftp frontend@localhost
    frontend@localhost's password:
    Connected to localhost.
    sftp> put test
    Uploading test to /test
    remote open("/test"): Permission denied
    sftp> ls
    uploads
    sftp> cd uploads/
    sftp> put test
    Uploading test to /uploads/test
    test                                                                                  100%   10     0.0KB/s   00:00


