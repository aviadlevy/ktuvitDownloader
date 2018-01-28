#!/usr/bin/env python
# -*- coding: utf-8 -*-

SCHEME = "http://"
URL = "wizdom.xyz/"
URL_JSON = SCHEME + "json." + URL
URL_ZIP = SCHEME + "zip." + URL

SUB_EXT = [".srt", ".sub"]
VIDEO_EXT = [".webm", ".mkv", ".flv", ".avi", ".mov", ".wmv", ".rm", ".rmvb", ".mp4", ".m4p", ".m4v", ".mpg", ".mpeg",
             "mp2", ".mpe", ".mpv", ".m2v", ".m4v"]
TORRENTS_GROUPS = ["[ettv]", "[eztv]", "[rartv]", "[P2PDL]", "[TJET]", "[EtHD]", "[PRiME]", "[VTV]", "[DDR]",
                   "[DSRG]", "[UTR]", "[GloDLS]", "[SexyTv]"]

CONFIG_FILE = ".ktuvitConfig.cfg"
LOG_FILE = ".ktuvitLogger.log"
CACHING_FILE = ".ktuvitCache.yml"

KB = 1024
MB = KB * 1024

CACHE_DAYS = 8
