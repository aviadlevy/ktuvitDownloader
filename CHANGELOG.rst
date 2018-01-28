ChangeLog
=========

4.0.0 (2018-01-xx)
------------------

- New sub provider: wizdom.xyz
- re-write major parts of the tool
- now supporting python 2 and python 3

3.0.1 (2017-08-16)
------------------

- bug fix

3.0.0 (2017-08-11)
------------------

- download subtitles using "subliminal" package.
  - NOTE: sometime the subtitles are machine translated. I'll try to recognize it in advance and not download such subtitles

2.0.5 (2017-06-15)
------------------

- NOTE: Ktuvit stopped working (redirect to sratim.co.il)
- Added -o argument to only organize you base folder

2.0.4 (2017-01-10)
------------------

- Minor bug fix

2.0.3 (2016-12-27)
------------------

- Minor bug fix
- Added more torrent groups

2.0.1 (2016-12-05)
------------------

- Minor bug fix

2.0.0 (2016-12-13)
------------------

- Ktuvit.com now using captcha, so I added selenium to let the user login by itself

1.2.1 (2016-12-05)
------------------

- Minor bug fix

1.2.0 (2016-11-24)
------------------

- Now all configuration/log/cache files will be saved on the common cache file
- New argument to display cache
- cache is now saved only for 8 days
- Added more torrent groups

1.1.0 (2016-11-14)
------------------

- Major caching improvement
- Minor detection improvement
- Rename files when file name contains torrent group (interfere with release group detection)

1.0.1 (2016-11-09)
------------------

- Don't save caching on specific run
- Don't save logs on specific run, instead print them to screen
- Make sure the cache is not exploding. clear it from files we've found already
- Cosmetic changes to the code

1.0.0 (2016-11-06)
------------------

- Caching is here! reduce the amount of API calls, and improve speed
- Added year to recognize the right title

0.2.2.0 (2016-10-25)
--------------------

- Add -s arg to download from specific location. you can give a specific file or specific directory, and you'll get only the sub file (without cleaning or moving) python

0.2.1.0 (2016-10-22)
--------------------

- Show less log on -l arg (only logs from last date used)
- Add -la arg to show all log file

0.2.0.3 (2016-10-20)
--------------------

- More ways to find subtitles
- Now the tool will delete all subtitle on startup assuming they english subs

0.2.0.2 (2016-10-06)
--------------------

- More chance to fund subtitles

0.2.0.0 - 0.2.0.1 (2016-08-30)
------------------------------

- More ways to find subtitles

0.1.1.0 (2016-08-29)
--------------------

- Minor cosmetic changes

0.0.1.4 (2016-08-24)
--------------------

- Added moving progress bar
- Change moving to copy-delete. see `Issue #1 <https://github.com/aviadlevy/ktuvitDownloader/issues/1>`_
- Now logger is rotating (on 1MB)

0.0.1.2-3 (2016-08-23)
----------------------

- Small bug fix causing the program to crash


0.0.1 (2016-08-21)
------------------

- Initial release
