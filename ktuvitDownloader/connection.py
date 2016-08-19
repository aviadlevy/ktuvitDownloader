#!/usr/bin/env python
# -*- coding: utf-8 -*-
import StringIO
import os
import re
import zipfile

from const import *
from ktuvitDownloader.CustomExceptions import *

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

import requests


def findBestUrl(allUrlSuff, movType):
    # find the first that match the type to our type
    for urlSuff in allUrlSuff:
        if ("tvshow" in urlSuff.find_next("img")["src"] and movType == "episode") or (
                        "movie" in urlSuff.find_next("img")["src"] and movType == "movie"):
            return urlSuff["href"]
    # TODO: need to enhanced this to really find the best one, and not just return the first
    # TODO: IMDB?
    return allUrlSuff[0]["href"]


def getHeaders():
    return {
        "Host":            "www.ktuvit.com", "Connection": "keep - alive", "Upgrade-Insecure-Requests": 1,
        "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/51.0.2704.103 Safari/537.36",
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q =0.8",
        "Accept-Encoding": "gzip,deflate,sdch", "Accept-Language": "en-US,en;q=0.8,he;q =0.6"
    }


def getSeEpId(num, htmlToParse, seOrEp):
    vidId = ""
    ids = BeautifulSoup(htmlToParse.text, "html.parser").find_all("a", id=lambda x: x and x.startswith(seOrEp))
    for i in ids:
        if int(i.text) == num:
            vidId = i["id"]
    return vidId


class Connection(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.s = requests.Session()

    def login(self):
        r = self.s.post(URL + URL_LOGIN, {"email": self.username, "password": self.password, "Login": "התחבר"})

        if LOGIN_ERROR in r.text.encode("utf-8"):
            raise WrongLoginException("Wrong username or password. "
                                      "please run \"ktuvitDownloader -r\" in order to "
                                      "reset the username and password you entered")
        if LOGIN_BLOCKED in r.text.encode("utf-8"):
            raise WrongLoginException("Your username probably blocked. you need to register again.")

    def download(self, fullTitle, data):

        loginRes = self.s.get(URL + URL_SEARCH + data["title"])

        allUrlSuff = BeautifulSoup(loginRes.text, "html.parser").find_all("a", {"itemprop": "url"})
        if len(allUrlSuff) > 1:
            # todo: find the best one
            urlSuff = findBestUrl(allUrlSuff, data["type"])
        else:
            try:
                urlSuff = allUrlSuff[0]["href"]
            except:
                raise Exception("Can't find this title: " + data["title"])

        if data["type"] == "episode":
            subDownloadPage = self.downloadEpSub(data, urlSuff)
        else:
            subDownloadPage = self.downloadMovSub(data, urlSuff)

        try:
            subId = BeautifulSoup(subDownloadPage.text, "html.parser").find("div",
                                                                            title=fullTitle).parent.find_previous_sibling(
                    "tr").find("a")["name"]
        except AttributeError:
            try:
                subId = BeautifulSoup(subDownloadPage.text, "html.parser").find_all("div",
                                                                                    title=lambda x: x and x.endswith(
                                                                                            data["release_group"]))[
                    0].parent.find_previous_sibling("tr").find("a")["name"]
            except Exception:
                # TODO: try to find another ways to find the subId
                # this is probably mean that the subtitle not here yet
                title = data["title"]
                if data["type"] == "episode":
                    title += "." + str(data["season"]) + "." + str(data["episode"])
                raise CantFindSubtitleException("Can't find subtitle id - for this title: " + title)
        except Exception as e:
            raise repr(e)
        if not subId:
            raise Exception("id is empty")

        subFileDownRes = self.s.get(URL + URL_DOWNLOAD, params={"id": subId}, stream=True)
        z = zipfile.ZipFile(StringIO.StringIO(subFileDownRes.content))
        for f in z.namelist():
            if os.path.splitext(f)[1] in SUB_EXT:
                return z.read(f).replace("\r\n", "\n"), os.path.splitext(f)[1]

    def downloadMovSub(self, data, urlSuff):
        urlSuffMatch = re.search("/tt1(\d+)/", urlSuff)
        if urlSuffMatch:
            urlSuff = urlSuffMatch.group(1)
        else:
            raise Exception("Can't find this title: " + data["title"] + "\n")

        subDownloadPage = self.s.get(URL + URL_AJAX + "?moviedetailssubtitles=" + urlSuff)
        with open("C:\\users\\win7\\desktop\\out1.html", "w") as f:
            f.write(BeautifulSoup(subDownloadPage.text, "html.parser").prettify(encoding="utf-8"))
        return subDownloadPage

    def downloadEpSub(self, data, urlSuff):
        resToParse = self.s.get(URL + urlSuff)
        seasonId = getSeEpId(data["season"], resToParse, "seasonlink_")
        if not seasonId:
            raise Exception("Can't find this season: " + str(data["season"]) + " - for this title: " + data["title"])

        seasonRes = self.s.post(URL + URL_AJAX, params={"seasonid": seasonId})
        episodeId = getSeEpId(data["episode"], seasonRes, "episodelink_")
        if not episodeId:
            raise Exception("Can't find this episode: " + str(data["season"]) + "." + str(
                    data["episode"]) + " - for this title: " + data["title"])

        epRes = self.s.post(URL + URL_AJAX, params={"episodedetails": episodeId})
        with open("C:\\users\\win7\\desktop\\out1.html", "w") as f:
            f.write(BeautifulSoup(epRes.text, "html.parser").prettify(encoding="utf-8"))
        return epRes

    def close(self):
        self.s.close()
