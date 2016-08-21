ktuvitDownloader
================
Auto-Download fron Ktuvit.com
-----------------------------

This package will allow you to auto-download subtitles from ktuvit.com website.

This is an Alpha version. use with caution.

Install:
::
  pip install ktuvitDownloader

Usage:
::
  ktuvitDownloader -h

Run:
::
  ktuvitDownloader
  
The "flow" is:
- scan *"base"* directory, and **clean** any files smaller than 750KB, or videos smaller than 30MB.
- search all video files on ktuvit.com and try to find best subtitle.
- if we found a match, download and move the video+subtitle to the *"dest"* directory.

TODO List:
---------
- Imporve cleaning of the "dest" directory. Add argument to choose whether you want to clean or not.
- Improve logging system
- Improve subtitle detection
- Create caching system
- Improve REASME.rst (this file)

:Author:
    Aviad Levy

:Version: 0.0.1
