#!/usr/bin/env python
# -*- coding: utf-8 -*-
import StringIO
import datetime
import json
import os
import zipfile

import requests
import yaml
from imdbpie import Imdb

from const import *
from files import clear_data_dir
from ktuvitDownloader.CustomExceptions import *


def find_best_sub(list_of_subs, data, title):
    # first, let's find same name
    for sub in list_of_subs:
        if sub.get("version", "") == title:
            return sub
    # then, let's try same group release
    for sub in list_of_subs:
        if sub.get("release_group", "").lower() == data.get("release_group", "").lower():
            return sub
    # then, some last chance logic
    for sub in list_of_subs:
        if sub.get("format", "").lower == data["format"].lower() and (
                sub.get("resolution", "").lower() == data.get("screen_size", "").lower() or sub.get(
                "video_codec").lower() == data.get("video_codec", "").lower()):
            return sub


def get_json_from_wizdom(imdb_id):
    res = requests.get(URL_JSON + imdb_id + ".json")
    if res.status_code == 200:
        return res.content


class Downloader(object):
    def __init__(self, app_dir, logger):
        self.app_dir_data = app_dir.user_data_dir
        self.cur_cache = {}
        self.cache = {}
        self.cache_file = os.path.join(app_dir.user_data_dir, CACHING_FILE)
        if os.path.exists(self.cache_file):
            with open(self.cache_file) as f:
                self.cache = yaml.load(f)
                if not self.cache:
                    self.cache = {}
        self.in_cache = []
        self.imdb = Imdb()
        self.logger = logger

    def download(self, data, full_title):
        key = data["title"]
        if data["type"] == "episode":
            key += "." + str(data["season"]) + "." + str(data["episode"])
        self.cur_cache = self.cache.get(key, {})
        imdb_id = self.get_imdb_id(data)

        self.save_cache(key)

        sub_json = self.get_sub_info(data, full_title, imdb_id)

        if not sub_json:
            self.sub_not_found_handler(data)

        z = self.get_sub_zip_file(sub_json)
        for f in z.namelist():
            if os.path.splitext(f)[1] in SUB_EXT:
                return self.get_sub_content(f, z)

    def get_sub_zip_file(self, sub_json):
        sub_file_down_res = requests.get(URL_ZIP + sub_json.get("id") + ".zip")
        return zipfile.ZipFile(StringIO.StringIO(sub_file_down_res.content))

    def get_sub_content(self, f, z):
        ret = z.read(f)
        try:
            ret = ret.encode("utf-8").replace("\r\n", "\n")
        except:
            ret = ret.replace("\r\n", "\n")
        return ret, os.path.splitext(f)[1]

    def sub_not_found_handler(self, data):
        title = data["title"]
        if data["type"] == "episode":
            title += "." + str(data["season"]) + "." + str(data["episode"])
        raise CantFindSubtitleException("Can't find subtitle id - for this title: " + title)

    def get_sub_info(self, data, full_title, imdb_id):
        json_from_wizdom = get_json_from_wizdom(imdb_id)
        if not json_from_wizdom:
            raise CantFindSubtitleException("wrong imdb id?")
        json_from_wizdom = json.loads(json_from_wizdom)
        self.logger.info("title from wizdom is: " + json_from_wizdom.get("title_en"))
        if data["type"] == "episode":
            return self.get_ep_sub(data, json_from_wizdom.get("subs", {}), full_title)
        else:
            return self.download_mov_sub(data, json_from_wizdom.get("subs", {}), full_title)

    def get_imdb_id(self, data):
        imdb_id = self.cur_cache.get("imdb_id", "")
        if not imdb_id:
            imdb_id = self.imdb.search_for_title(data["title"])[0].get("imdb_id")
            self.cur_cache["imdb_id"] = imdb_id
        self.logger.info("imdb_id is: " + imdb_id)
        return imdb_id

    def download_mov_sub(self, data, wizdom_json, full_title):
        return find_best_sub(wizdom_json, data, full_title)

    def get_ep_sub(self, data, wizdom_json, full_title):
        season_json = wizdom_json.get(str(data["season"]), {})
        if season_json:
            episode_json = season_json.get(str(data["episode"]), {})
            if episode_json:
                return find_best_sub(episode_json, data, full_title)
            raise CantFindSubtitleException("can't find episode: " + data["episode"])
        raise CantFindSubtitleException("can't find season: " + data["season"])

    def close(self, specific):
        if not specific:
            self.clear_cache()
            with open(self.cache_file, "wb") as f:
                yaml.dump(self.cache, f)
        clear_data_dir(self.app_dir_data)

    def clear_cache(self):
        for k, v in self.cache.items():
            try:
                if k not in self.in_cache and v["time_stamp"] < datetime.datetime.now() - datetime.timedelta(
                        CACHE_DAYS):
                    self.cache.pop(k)
            except KeyError:
                self.cache.pop(k)

    def save_cache(self, key):
        self.in_cache.append(key)
        self.in_cache = list(set(self.in_cache))
        self.cur_cache["time_stamp"] = datetime.datetime.now()
        self.cache[key] = self.cur_cache
