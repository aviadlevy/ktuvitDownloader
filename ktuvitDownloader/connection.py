#!/usr/bin/env python
# -*- coding: utf-8 -*-
import StringIO
import os
import re
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
        "Host":            "www.ktuvit.com", "Connection": "keep - alive", "Upgrade-Insecure-Requests": 1,
        "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/51.0.2704.103 Safari/537.36",
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q =0.8",
        "Accept-Encoding": "gzip,deflate,sdch", "Accept-Language": "en-US,en;q=0.8,he;q =0.6"
    }


def getSeEpId(num, htmlToParse, seOrEp):
    id = ""
    ids = BeautifulSoup(htmlToParse.text, "html.parser").find_all("a", id=lambda x: x and x.startswith(seOrEp))
    for i in ids:
        if int(i.text) == num:
            id = i["id"]
    return id


class Connection(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.s = requests.Session()

    def login(self):
        self.s.post(URL + URL_LOGIN, {"email": self.username, "password": self.password, "Login": "התחבר"})

    def download(self, fullTitle, data):
        print data
        r = self.s.get(URL + URL_SEARCH + data["title"])
        # with open("C:\\users\\win7\\desktop\\out.html", 'w') as f:
        #     f.write(BeautifulSoup(r.text, "html.parser").prettify(encoding='utf-8'))
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
                raise Exception("Can't find this title: " + data["title"] + "\n" + repr(e))

        if data["type"] == "episode":
            subDownloadPage = self.downloadEpSub(data, urlSuff)
        else:
            subDownloadPage = self.downloadMovSub(data, urlSuff)

        subId = ""
        try:
            subId = BeautifulSoup(subDownloadPage.text, "html.parser").find("div",
                    title=fullTitle).parent.find_previous_sibling("tr").find("a")["name"]
        except AttributeError as e:
            try:
                subId = BeautifulSoup(subDownloadPage.text, "html.parser").find_all("div",
                        title=lambda x: x and x.endswith(data['release_group']))[0].parent.find_previous_sibling(
                    "tr").find("a")["name"]
            except Exception as e:
                raise Exception("Can't find subtitle id\n\n" + repr(e))
        except Exception as e:
            raise repr(e)
        if not subId:
            raise Exception("id is empty")

        print subId

        r5 = self.s.get(URL + URL_DOWNLOAD, params={'id': subId}, stream=True)
        print r5.headers
        z = zipfile.ZipFile(StringIO.StringIO(r5.content))
        for n in z.namelist():
            print os.path.splitext(n)[0]
            print os.path.splitext(n)[1]
            if os.path.splitext(n)[1] in SUB_EXT:
                # print z.read(n)
                # TODO: this is the file!
                pass

    def downloadMovSub(self, data, urlSuff):
        urlSuffMatch = re.search("/tt1(\d+)/", urlSuff)
        if urlSuffMatch:
            urlSuff = urlSuffMatch.group(1)
        else:
            raise Exception("Can't find this title: " + data["title"] + "\n")
        subDownloadPage = self.s.get(URL + URL_AJAX + "?moviedetailssubtitles=" + urlSuff)
        with open("C:\\users\\win7\\desktop\\out1.html", 'w') as f:
            f.write(BeautifulSoup(subDownloadPage.text, "html.parser").prettify(encoding='utf-8'))
        return subDownloadPage

    def downloadEpSub(self, data, urlSuff):
        resToParse = self.s.get(URL + urlSuff)
        seasonId = getSeEpId(data["season"], resToParse, "seasonlink_")
        print seasonId
        if not seasonId:
            raise Exception("Can't find this season: " + str(data["season"]) + " - for this title: " + data["title"])
        r4 = self.s.post(URL + URL_AJAX, params={"seasonid": seasonId})
        episodeId = getSeEpId(data["episode"], r4, "episodelink_")
        print episodeId
        if not episodeId:
            raise Exception("Can't find this episode: " + str(data["season"]) + " - for this title: " + data["title"])
        r3 = self.s.post(URL + URL_AJAX, params={"episodedetails": episodeId})
        with open("C:\\users\\win7\\desktop\\out1.html", 'w') as f:
            f.write(BeautifulSoup(r3.text, "html.parser").prettify(encoding='utf-8'))
        return r3

    def close(self):
        self.s.close()
