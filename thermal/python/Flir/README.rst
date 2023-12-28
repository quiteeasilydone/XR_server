Easy to use Python module to extract FLIR metadata from jpeg files

Installation
************

PyPI
====
The recommended process is to install the `PyPI package <https://pypi.python.org/pypi/ExifRead>`_,
as it allows easily staying up to date::

    $ pip install exifread

Python Script
=============
::

    import Flir_Extractor
    # Open image file for reading (binary mode)
    f = open(path_name, 'rb')

    # Return Flir tags
    tags = Flir_Extractor.process_file(f)

Returned tags will be a dictionary mapping names of Flir tags to their
values in the file named by path_name.
You can process the tags as you wish. In particular, you can iterate through all the tags with::

Tag Descriptions
****************

Tags are divided into these main categories:

- ``FLIR``: https://exiftool.org/TagNames/FLIR.html
