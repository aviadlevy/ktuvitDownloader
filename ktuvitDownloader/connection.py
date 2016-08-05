#!/usr/bin/env python
# -*- coding: utf-8 -*-
import StringIO
import os
import zipfile

from const import *

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

import requests


def findBestUrl(allUrlSuff):
    pass


def getHeaders():
    return {
        "Host":                      "www.ktuvit.com",
        "Connection":                "keep - alive",
        "Upgrade-Insecure-Requests": 1,
        "User-Agent":                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                     "Chrome/51.0.2704.103 Safari/537.36",
        "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q =0.8",
        "Accept-Encoding":           "gzip,deflate,sdch",
        "Accept-Language":           "en-US,en;q=0.8,he;q =0.6"
    }


class Connection(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.s = requests.Session()

    def login(self):
        self.s.post(URL + URL_LOGIN, {"email": self.username, "password": self.password, "Login": "התחבר"})

    def download(self, data):
        print data
        r = self.s.get(URL + "/browse.php?speechval=&q=" + data["title"])
        # todo: search for <a href="...." itemprop="url">
        allUrlSuff = BeautifulSoup(r.text, "html.parser").find_all('a', {'itemprop': 'url'})
        if len(allUrlSuff) > 1:
            # todo: find the best one
            urlSuff = findBestUrl(allUrlSuff)
            pass
        else:
            try:
                urlSuff = allUrlSuff[0]["href"]
            except Exception as e:
                raise "Can't find this title: " + data["title"]

        r2 = self.s.get(URL + urlSuff)
        with open("C:\\users\\win7\\desktop\\out.html", 'w') as f:
            f.write(BeautifulSoup(r2.text, "html.parser").prettify(encoding='utf-8'))
        r3 = self.s.post(URL + URL_AJAX, params={"episodedetails": "152847"})

        with open("C:\\users\\win7\\desktop\\out1.html", 'w') as f:
            f.write(BeautifulSoup(r3.text, "html.parser").prettify(encoding='utf-8'))

        # todo: extract the id for downloadsubtitile.php

        r4 = self.s.get(URL + URL_DOWNLOAD, params={'id': '305835'},
                        stream=True)
        print r4.headers
        z = zipfile.ZipFile(StringIO.StringIO(r4.content))
        for n in z.namelist():
            print os.path.splitext(n)[1]
            if os.path.splitext(n)[1] in SUB_EXT:
                # print z.read(n)
                # TODO: this is the file!
                pass

    def close(self):
        self.s.close()
