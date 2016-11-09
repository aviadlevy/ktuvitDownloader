#!/usr/bin/env python
# -*- coding: utf-8 -*-
import StringIO
import os
import re
import zipfile

from guessit import guessit
import yaml

from const import *
from ktuvitDownloader.CustomExceptions import *

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

import requests


def find_best_url(all_url_suff, mov_type, year):
    best_option = None
    for url_suff in all_url_suff:
        if ("tvshow" in url_suff.find_next("img")["src"] and mov_type == "episode") or (
                        "movie" in url_suff.find_next("img")["src"] and mov_type == "movie"):
            if year and year == url_suff.find_next("span").text:
                return url_suff["href"]
            elif best_option:
                continue
            else:
                best_option = url_suff["href"]
    if best_option:
        return best_option
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


def get_id_with_reg(html_parsed):
    reg_id = html_parsed.parent.find_previous("tr").find("a")["href"]
    isMatch = re.match(r"/downloadsubtitle\.php\?id=(\d+)", reg_id)
    if isMatch:
        sub_id = isMatch.group(1)
        return sub_id
    return None


def get_lang(html_parsed):
    return html_parsed.parent.find_previous("div").find_previous("div").find("img")["title"].encode("utf-8")


class Connection(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.s = requests.Session()
        self.cur_cache = {}
        self.cache = {}
        if os.path.exists(CACHING_FILE):
            with open(CACHING_FILE) as f:
                self.cache = yaml.load(f)
                if not self.cache:
                    self.cache = {}
        self.in_cache = []

    def login(self):
        r = self.s.post(URL + URL_LOGIN, {"email": self.username, "password": self.password, "Login": "התחבר"})

        if LOGIN_ERROR in r.text.encode("utf-8"):
            raise WrongLoginException("Wrong username or password. "
                                      "please run \"ktuvitDownloader -r\" in order to "
                                      "reset the username and password you entered")
        if LOGIN_BLOCKED in r.text.encode("utf-8"):
            raise WrongLoginException("Your username probably blocked. you need to register again.")

    def download(self, full_title, data):
        key = data["title"]
        if data["type"] == "episode":
            key += "." + str(data["season"]) + "." + str(data["episode"])
        self.cur_cache = self.cache.get(key, {})
        if not self.cur_cache.get("url_suff"):
            login_res = self.s.get(URL + URL_SEARCH + data["title"])

            all_url_suff = BeautifulSoup(login_res.text, "html.parser").find_all("a", {"itemprop": "url"})
            if len(all_url_suff) > 1:
                # todo: find the best one
                url_suff = find_best_url(all_url_suff, data["type"], data.get("year"))
            else:
                try:
                    url_suff = all_url_suff[0]["href"]
                except:
                    raise Exception("Can't find this title: " + data["title"])
            self.cur_cache["url_suff"] = url_suff
        else:
            url_suff = self.cur_cache["url_suff"]

        self.save_cache(key)

        if data["type"] == "episode":
            sub_download_page = self.download_ep_sub(data, url_suff)
            self.save_cache(key)
        else:
            sub_download_page = self.download_mov_sub(data, url_suff)

        sub_id = None

        try:
            html_sub_download = BeautifulSoup(sub_download_page.text, "html.parser")
            try:
                sub_id = html_sub_download.find("div", title=full_title).parent.find_previous_sibling("tr").find("a")[
                    "name"]
            except AttributeError:
                sub_id = get_id_with_reg(html_sub_download.find("div", title=full_title))
            try:
                lang = get_lang(html_sub_download.find("div", title=full_title))
                if lang != "עברית":
                    sub_id = None
            except AttributeError:
                pass
        except AttributeError:
            try:
                html_sub_download = BeautifulSoup(sub_download_page.text, "html.parser")
                sub_id = get_id_with_reg(
                        html_sub_download.find_all("div", title=lambda x: x and x.endswith(data["release_group"]))[0])
                try:
                    lang = get_lang(html_sub_download.find_all(
                            "div", title=lambda x: x and x.endswith(data["release_group"]))[0])
                    if lang != "עברית":
                        sub_id = None
                except AttributeError:
                    pass
            except (AttributeError, IndexError):
                try:
                    html_sub_download = BeautifulSoup(sub_download_page.text, "html.parser")
                    titles = html_sub_download.find_all("div")
                    for title in titles:
                        try:
                            sub_data = guessit(title["title"])
                            if sub_data["format"] == data["format"] and (
                                    sub_data["screen_size"] == data["screen_size"] or sub_data["video_codec"] == data[
                                "video_codec"]) and get_lang(title) == "עברית":
                                sub_id = get_id_with_reg(title)
                                if sub_id:
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
        if not self.cur_cache.get("season_id"):
            res_to_parse = self.s.get(URL + url_suff)
            season_id = get_se_ep_id(data["season"], res_to_parse, "seasonlink_")
            if not season_id:
                raise Exception("Can't find this season: " +
                                str(data["season"]) + " - for this title: " + data["title"])
            self.cur_cache["season_id"] = season_id
        else:
            season_id = self.cur_cache["season_id"]

        if not self.cur_cache.get("episode_id"):
            season_res = self.s.post(URL + URL_AJAX, params={"seasonid": season_id})
            episode_id = get_se_ep_id(data["episode"], season_res, "episodelink_")
            if not episode_id:
                raise Exception(
                    "Can't find this episode: " + str(data["season"]) + "." +
                    str(data["episode"]) + " - for this title: " + data["title"])
            self.cur_cache["episode_id"] = episode_id
        else:
            episode_id = self.cur_cache["episode_id"]

        ep_res = self.s.post(URL + URL_AJAX, params={"episodedetails": episode_id})
        return ep_res

    def close(self, specific):
        if not specific:
            self.clear_cache()
            with open(CACHING_FILE, "wb") as f:
                yaml.dump(self.cache, f)
        self.s.get(URL + URL_LOGOUT)
        self.s.close()

    def clear_cache(self):
        for k in self.cache.keys():
            if k not in self.in_cache:
                self.cache.pop(k)

    def save_cache(self, key):
        self.in_cache.append(key)
        self.in_cache = list(set(self.in_cache))
        self.cache[key] = self.cur_cache
