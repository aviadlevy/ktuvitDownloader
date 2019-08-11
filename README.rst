ktuvitDownloader
================

Auto-Download from Wizdom.xyz
-----------------------------

.. image:: http://img.shields.io/pypi/v/ktuvitDownloader.svg
    :target: https://pypi.python.org/pypi/ktuvitDownloader
    :alt: Latest Version


.. image:: http://img.shields.io/badge/license-LGPLv3-blue.svg
    :target: https://pypi.python.org/pypi/ktuvitDownloader
    :alt: LGPLv3 License


This package will allow you to auto-download hebrew subtitles from the israeli site wizdom.xyz website.


Install
-------

Install with `pip <http://www.pip-installer.org/>`_::

    $ pip install ktuvitDownloader

Upgrade
-------

Upgrade with `pip <http://www.pip-installer.org/>`_::

    $ pip install ktuvitDownloader --upgrade

Run
---

Just run cmd (WinKey + R, then type *cmd* and Enter) then::

    $ ktuvitDownloader
  

Usage
-----

Just run cmd (WinKey + R, then type *cmd* and Enter) then::

    $ ktuvitDownloader -h

The "flow" is:

- scan *"base"* directory, and **clean** any files smaller than 750KB, or videos smaller than 30MB.
- search all video files on wizdom.xyz and try to find best subtitle.
- if we found a match, download and move the video+subtitle to the *"dest"* directory.

TODO List:
----------
- Imporve cleaning of the "dest" directory. Add argument to choose whether you want to clean or not.
- add linux support
- Some case that subtitle text is jibrish

:Author:
    Aviad Levy

:Version: 4.0.2

:License: `LGPLv3 license <http://www.gnu.org/licenses/lgpl.html>`_
