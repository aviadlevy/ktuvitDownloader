#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import base64
import json
import logging
import os
import sys
from datetime import datetime
from getpass import getpass
from logging import handlers
from time import sleep

import yaml
from appdirs import AppDirs
from guessit import guessit

from ktuvitDownloader.CustomExceptions import CantFindSubtitleException, WrongLoginException
from ktuvitDownloader.__version__ import __version__
from ktuvitDownloader.connection import Connection
from ktuvitDownloader.const import *
from ktuvitDownloader.files import get_paths_files, move_finshed
from ktuvitDownloader.options import args_parse, parse_log

config = ConfigParser.RawConfigParser()
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
    logger.addHandler(get_handler(not options.specific))
    logger.setLevel(logging.INFO)

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

    if not os.path.isfile(config_file):
        options.reset = True

    if options.reset:
        if not options.specific:
            options.base_path = True
            options.dest_path = True

    if options.specific:
        base_dir = options.specific
        if not os.path.isdir(base_dir):
            ext = os.path.splitext(base_dir)[1]
            if ext not in VIDEO_EXT:
                print "The path you supplied  is not known video format.\nPlease try again."
                exit(-1)
            else:
                file_name = base_dir.split("\\")[-1]
                base_dir = os.path.dirname(os.path.realpath(base_dir))
                dest_dir = os.path.abspath(os.path.join(base_dir, os.pardir))
                config.read(config_file)
                downloader(base_dir, dest_dir, {os.path.join(base_dir, file_name): guessit(file_name)}, specific=True)
                exit(0)
        dest_dir = os.path.abspath(os.path.join(base_dir, os.pardir))

    if options.base_path:
        base_dir = raw_input("Enter the path to base directory (where all your files are): ")
        while not os.path.isdir(base_dir):
            print "Can't find this directory."
            base_dir = raw_input("Try again: ")
        try:
            config.add_section("Directories")
        except ConfigParser.DuplicateSectionError:
            pass
        config.set("Directories", "base_dir", base_dir)
        with open(config_file, "wb") as f:
            config.write(f)

    if options.dest_path:
        dest_dir = raw_input("Enter the path to dest directory (where you want to move your files. it can be the "
                             "same as base): ")
        while not os.path.isdir(dest_dir):
            print "Can't find this directory."
            dest_dir = raw_input("Try again: ")
        try:
            config.set("Directories", "dest_dir", dest_dir)
        except ConfigParser.DuplicateSectionError:
            pass
        with open(config_file, "wb") as f:
            config.write(f)

    config.read(config_file)
    if not options.specific:
        base_dir = config.get("Directories", "base_dir")
        dest_dir = config.get("Directories", "dest_dir")

    files = get_paths_files(base_dir, to_clean=not options.specific)

    if options.organize:
        print "Goodbye..."
        sleep(2)
        exit(1)

    downloader(base_dir, dest_dir, files, options.specific)


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
        print "Nothing to show"
    else:
        with open(cache_file) as f:
            text = yaml.load(f)
        if not text:
            print "Nothing to show"
        else:
            print json.dumps(text, default=json_serial, indent=4, ensure_ascii=False)


def print_configuration():
    if not os.path.isfile(config_file):
        print "Nothing to show"
    else:
        with open(config_file) as f:
            text = f.read()
        if not text:
            print "Nothing to show"
        else:
            print text


def print_log(isShort):
    if not os.path.isfile(log_file):
        print "Nothing to show"
    else:
        with open(log_file) as f:
            if isShort:
                text = f.readlines()
                text = parse_log(text)
            else:
                text = f.read()
        if not text:
            print "Nothing to show"
        else:
            print text


def print_version():
    print("+-------------------------------------------------------+")
    print("+               ktuvitDownloader " + __version__ + (23 - len(__version__)) * " " + "+")
    print("+-------------------------------------------------------+")
    print("|      Please report any bug or feature request at      |")
    print("| https://github.com/aviadlevy/ktuvitDownloader/issues  |")
    print("+-------------------------------------------------------+")


def get_handler(isFile):
    formatter = logging.Formatter(fmt="%(asctime)s\t%(levelname)s: %(message)s")
    if isFile:
        handler = handlers.RotatingFileHandler(filename=log_file, maxBytes=MB)
    else:
        handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    return handler


def downloader(base_dir, dest_dir, files, specific=False):
    downloaded = []
    con = Connection(app_dir)
    for path, data in files.items():
        try:
            vid_ext = os.path.splitext(path)[1]
            generic_path = os.path.splitext(path)[0]
            con.download(path)
            logger.info("Found " + generic_path + "!")
            print "Found", generic_path.split("\\")[-1]
            downloaded.append((generic_path, vid_ext))
        except CantFindSubtitleException as e:
            logger.warn(e)
        except Exception as e:
            logger.error(repr(e))
    if move_finshed(downloaded, base_dir, dest_dir):
        print "\n\nDone! check your Dest folder. you may find surprise\nTry again in a few hours, to prevent the " \
              "chance you'll get ban"
    else:
        print "Done! try again in a few hours, to prevent the chance you'll get ban"


if __name__ == "__main__":
    main()
