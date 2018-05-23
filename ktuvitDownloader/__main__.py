#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import json
import logging
import os
import sys
from datetime import datetime
from logging import handlers
from time import sleep

from six.moves import configparser
import yaml
from appdirs import AppDirs
from guessit import guessit
from six.moves import input, range

from ktuvitDownloader.CustomExceptions import CantFindSubtitleException
from ktuvitDownloader.__version__ import __version__
from ktuvitDownloader.const import *
from ktuvitDownloader.downloader import Downloader
from ktuvitDownloader.files import get_paths_files, move_finshed
from ktuvitDownloader.options import args_parse, parse_log
from io import open

config = configparser.RawConfigParser()

app_dir = AppDirs("ktuvitdownloader")
config_file = os.path.join(app_dir.user_data_dir, CONFIG_FILE)
log_file = os.path.join(app_dir.user_data_dir, LOG_FILE)
cache_file = os.path.join(app_dir.user_data_dir, CACHING_FILE)


def main():
    """
    main function
    """
    options = args_parse.parse_args()
    check_user_data_dir()
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handlers())
    if options.verbose:
        logger.addHandler(get_console_handlers())

    base_dir = ""
    dest_dir = ""

    if options.show_version:
        print_version()
        exit(0)

    if options.show_log:
        print_log(isShort=True)
        exit(0)

    if options.show_all_log:
        print_log(isShort=False)
        exit(0)

    if options.show_configuration:
        print_configuration()
        exit(0)

    if options.show_cache:
        print_cache()
        exit(0)

    logger.info("Starting...")

    if not os.path.isfile(config_file):
        options.reset = True
    else:
        config.read(config_file)
        if not config.has_section("Directories"):
            options.reset = True

    if options.reset:
        if not options.specific:
            options.base_path = True
            options.dest_path = True

    if options.specific:
        base_dir, dest_dir = handle_specific(options)

    if options.base_path:
        base_dir = handle_dir("base_dir")

    if options.dest_path:
        dest_dir = handle_dir("dest_dir")

    if not options.specific:
        base_dir = config.get("Directories", "base_dir")
        dest_dir = config.get("Directories", "dest_dir")

    logger.info("Organizing files...")
    files = get_paths_files(base_dir, to_clean=not options.specific)

    if options.organize:
        print("Goodbye...")
        sleep(2)
        exit(1)

    logger.info("Searching for subtitles...")
    download_handler(base_dir, dest_dir, files, options.specific)


def handle_dir(dir_str):
    dir = input("Enter the path to " + dir_str + ": ")
    while not os.path.isdir(dir):
        print("Can't find this directory.")
        dir = input("Try again: ")
    try:
        if not config.has_section("Directories"):
            config.add_section("Directories")
        config.set(u"Directories", dir_str, dir)
    except configparser.DuplicateSectionError:
        pass
    with open(config_file, "wb") as f:
        config.write(f)
    return dir


def handle_specific(options):
    base_dir = options.specific
    if not os.path.isdir(base_dir):
        ext = os.path.splitext(base_dir)[1]
        if ext not in VIDEO_EXT:
            print("The path you supplied  is not known video format.\nPlease try again.")
            exit(-1)
        else:
            file_name = base_dir.split("\\")[-1]
            base_dir = os.path.dirname(os.path.realpath(base_dir))
            dest_dir = os.path.abspath(os.path.join(base_dir, os.pardir))
            config.read(config_file)
            download_handler(base_dir, dest_dir, {
                os.path.join(base_dir, file_name): guessit(file_name)
            }, specific=True)
            exit(0)
    dest_dir = os.path.abspath(os.path.join(base_dir, os.pardir))
    return base_dir, dest_dir


def check_user_data_dir():
    app_dir_list = app_dir.user_data_dir.split("\\")
    for i in range(1, len(app_dir_list)):
        if not os.path.exists("\\".join(app_dir_list[:i + 1])):
            os.mkdir("\\".join(app_dir_list[:i + 1]))


def print_cache():
    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial
        raise TypeError("Type not serializable")

    if not os.path.isfile(cache_file):
        print("Nothing to show")
    else:
        with open(cache_file) as f:
            text = yaml.load(f)
        if not text:
            print("Nothing to show")
        else:
            print(json.dumps(text, default=json_serial, indent=4, ensure_ascii=False))


def print_configuration():
    if not os.path.isfile(config_file):
        print("Nothing to show")
    else:
        with open(config_file) as f:
            text = f.read()
        if not text:
            print("Nothing to show")
        else:
            print(text)


def print_log(isShort):
    if not os.path.isfile(log_file):
        print("Nothing to show")
    else:
        with open(log_file) as f:
            if isShort:
                text = f.readlines()
                text = parse_log(text)
            else:
                text = f.read()
        if not text:
            print("Nothing to show")
        else:
            print(text)


def print_version():
    print("+-------------------------------------------------------+")
    print("+               ktuvitDownloader " + __version__ + (23 - len(__version__)) * " " + "+")
    print("+-------------------------------------------------------+")
    print("|      Please report any bug or feature request at      |")
    print("| https://github.com/aviadlevy/ktuvitDownloader/issues  |")
    print("+-------------------------------------------------------+")


def get_file_handlers():
    formatter = logging.Formatter(fmt="%(asctime)s\t%(levelname)s: %(message)s")
    file_handler = handlers.RotatingFileHandler(filename=log_file, maxBytes=MB)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    return file_handler


def get_console_handlers():
    formatter = logging.Formatter(fmt="%(asctime)s\t%(levelname)s: %(message)s")
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    return stream_handler


def download_handler(base_dir, dest_dir, files, specific=False):
    downloaded = []
    downloader = Downloader(app_dir, logger)
    for path, data in files.items():
        try:
            one_download_handler(downloader, data, downloaded, path)
        except CantFindSubtitleException as e:
            logger.warn(e)
        except Exception as e:
            logger.error(repr(e))
    downloader.close(specific)
    if move_finshed(downloaded, base_dir, dest_dir):
        print("\n\nDone! check your Dest folder. you may find a surprise...")
    else:
        print("Done!")


def one_download_handler(downloader, data, downloaded, path):
    vid_ext = os.path.splitext(path)[1]
    generic_path = os.path.splitext(path)[0]
    sub_file, sub_ext = downloader.download(data, generic_path.split("\\")[-1])
    logger.info("Found " + path + "!")
    print("Found", path.split("\\")[-1])
    with open(generic_path + sub_ext, "wb") as f:
        try:
            f.write(sub_file.encode('utf-8'))
        except:
            f.write(sub_file)
    downloaded.append((generic_path, sub_ext, vid_ext))


if __name__ == "__main__":
    main()
