#!/usr/bin/env python
# -*- coding: utf-8 -*-
import StringIO
import os
import re
import zipfile

from guessit import guessit

from const import *
from ktuvitDownloader.CustomExceptions import *

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

import requests


def find_best_url(all_url_suff, mov_type):
    # find the first that match the type to our type
    for url_suff in all_url_suff:
        if ("tvshow" in url_suff.find_next("img")["src"] and mov_type == "episode") or (
                        "movie" in url_suff.find_next("img")["src"] and mov_type == "movie"):
            return url_suff["href"]
    # TODO: need to enhanced this to really find the best one, and not just return the first
    # TODO: IMDB?
    return all_url_suff[0]["href"]


def get_headers():
    return {
        "Host":            "www.ktuvit.com", "Connection": "keep - alive", "Upgrade-Insecure-Requests": 1,
        "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/51.0.2704.103 Safari/537.36",
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q =0.8",
        "Accept-Encoding": "gzip,deflate,sdch", "Accept-Language": "en-US,en;q=0.8,he;q =0.6"
    }


def get_se_ep_id(num, html_to_parse, se_or_ep):
    vid_id = ""
    ids = BeautifulSoup(html_to_parse.text, "html.parser").find_all("a", id=lambda x: x and x.startswith(se_or_ep))
    for i in ids:
        if int(i.text) == num:
            vid_id = i["id"]
    return vid_id


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

    def download(self, full_title, data):
        login_res = self.s.get(URL + URL_SEARCH + data["title"])

        all_url_suff = BeautifulSoup(login_res.text, "html.parser").find_all("a", {"itemprop": "url"})
        if len(all_url_suff) > 1:
            # todo: find the best one
            url_suff = find_best_url(all_url_suff, data["type"])
        else:
            try:
                url_suff = all_url_suff[0]["href"]
            except:
                raise Exception("Can't find this title: " + data["title"])

        if data["type"] == "episode":
            sub_download_page = self.download_ep_sub(data, url_suff)
        else:
            sub_download_page = self.download_mov_sub(data, url_suff)

        sub_id = None

        try:
            html_sub_download = BeautifulSoup(sub_download_page.text, "html.parser")
            sub_id = html_sub_download.find("div", title=full_title).parent.find_previous_sibling("tr").find("a")["name"]
        except AttributeError:
            try:
                html_sub_download = BeautifulSoup(sub_download_page.text, "html.parser")
                sub_id = html_sub_download.find_all("div", title=lambda x: x and x.endswith(data["release_group"]))[
                    0].parent.find_previous_sibling("tr").find("a")["name"]
            except (AttributeError, IndexError):
                try:
                    html_sub_download = BeautifulSoup(sub_download_page.text, "html.parser")
                    titles = html_sub_download.find_all("div")
                    for title in titles:
                        try:
                            sub_data = guessit(title["title"])
                            if sub_data["format"] == data["format"] and sub_data["screen_size"] == data["screen_size"]:
                                sub_id = title.parent.find_previous_sibling("tr").find("a")["name"]
                                break
                        except KeyError:
                            pass
                except Exception:
                    # this is probably mean that the subtitle not here yet
                    sub_id = None
        except Exception as e:
            raise repr(e)
        if not sub_id:
            title = data["title"]
            if data["type"] == "episode":
                title += "." + str(data["season"]) + "." + str(data["episode"])
            raise CantFindSubtitleException("Can't find subtitle id - for this title: " + title)

        sub_file_down_res = self.s.get(URL + URL_DOWNLOAD, params={"id": sub_id}, stream=True)
        z = zipfile.ZipFile(StringIO.StringIO(sub_file_down_res.content))
        for f in z.namelist():
            if os.path.splitext(f)[1] in SUB_EXT:
                ret = z.read(f)
                try:
                    ret = ret.encode("utf-8").replace("\r\n", "\n")
                except:
                    ret = ret.replace("\r\n", "\n")
                return ret, os.path.splitext(f)[1]

    def download_mov_sub(self, data, url_suff):
        url_suff_match = re.search("/tt1(\d+)/", url_suff)
        if url_suff_match:
            url_suff = url_suff_match.group(1)
        else:
            raise Exception("Can't find this title: " + data["title"] + "\n")

        sub_download_page = self.s.get(URL + URL_AJAX + "?moviedetailssubtitles=" + url_suff)
        return sub_download_page

    def download_ep_sub(self, data, url_suff):
        res_to_parse = self.s.get(URL + url_suff)
        season_id = get_se_ep_id(data["season"], res_to_parse, "seasonlink_")
        if not season_id:
            raise Exception("Can't find this season: " + str(data["season"]) + " - for this title: " + data["title"])

        season_res = self.s.post(URL + URL_AJAX, params={"seasonid": season_id})
        episode_id = get_se_ep_id(data["episode"], season_res, "episodelink_")
        if not episode_id:
            raise Exception("Can't find this episode: " + str(data["season"]) + "." + str(
                    data["episode"]) + " - for this title: " + data["title"])

        ep_res = self.s.post(URL + URL_AJAX, params={"episodedetails": episode_id})
        return ep_res

    def close(self):
        self.s.get(URL + URL_LOGOUT)
        self.s.close()
