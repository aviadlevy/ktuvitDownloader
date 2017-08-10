#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from babelfish import Language
from subliminal import download_best_subtitles, region, save_subtitles, scan_video

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


class Connection(object):
    def __init__(self, dir):
        if not os.path.exists(dir.user_cache_dir):
            os.mkdir(dir.user_cache_dir)
        self.configuration_dir = dir.user_cache_dir
        # configure the cache
        region.configure('dogpile.cache.dbm', arguments={
            'filename': os.path.join(self.configuration_dir, 'cachefile.dbm')
            })

    def download(self, path):

        video = scan_video(path)

        # download best subtitles
        subtitles = download_best_subtitles([video], {Language('heb')})

        # save them to disk, next to the video
        subtitle = save_subtitles(video, subtitles[video], single=True)

        return subtitle[0]
