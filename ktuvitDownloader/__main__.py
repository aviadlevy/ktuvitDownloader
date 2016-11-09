#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import base64
import logging
import os
from getpass import getpass
from logging import handlers

import sys
from guessit import guessit

from ktuvitDownloader.CustomExceptions import CantFindSubtitleException, WrongLoginException
from ktuvitDownloader.__version__ import __version__
from ktuvitDownloader.connection import Connection
from ktuvitDownloader.const import *
from ktuvitDownloader.files import get_paths_files, move_finshed
from ktuvitDownloader.options import args_parse, parse_log

config = ConfigParser.RawConfigParser()


def main():
    """
    main function
    """
    options = args_parse.parse_args()
    global logger
    logger = logging.getLogger()
    logger.addHandler(get_handler(not options.specific))
    logger.setLevel(logging.INFO)

    base_dir = ""
    dest_dir = ""

    if options.version:
        print_version()
        exit(0)

    if options.show_log:
        print_log(isShort=True)
        exit(0)

    if options.show_all_log:
        print_log(isShort=False)
        exit(0)

    if options.configuration:
        print_configuration()
        exit(0)

    if not os.path.isfile(CONFIG_FILE):
        options.reset = True

    if options.reset:
        get_login_credential()
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
                config.read(CONFIG_FILE)
                username = config.get("Login", "username")
                password = base64.b64decode(config.get("Login", "password"))
                downloader(base_dir, dest_dir, {os.path.join(base_dir, file_name): guessit(file_name)}, username,
                           password, specific=True)
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
        with open(CONFIG_FILE, "wb") as f:
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
        with open(CONFIG_FILE, "wb") as f:
            config.write(f)

    config.read(CONFIG_FILE)
    username = config.get("Login", "username")
    password = base64.b64decode(config.get("Login", "password"))
    if not options.specific:
        base_dir = config.get("Directories", "base_dir")
        dest_dir = config.get("Directories", "dest_dir")

    files = get_paths_files(base_dir, to_clean=not options.specific)

    downloader(base_dir, dest_dir, files, username, password, options.specific)


def print_configuration():
    if not os.path.isfile(CONFIG_FILE):
        print "Nothing to show"
    else:
        with open(CONFIG_FILE) as f:
            text = f.read()
            if not text:
                print "Nothing to show"
            else:
                print text
                config.read(CONFIG_FILE)
                c_password = base64.b64decode(config.get("Login", "password"))
                print "Decoded password:", c_password


def print_log(isShort):
    if not os.path.isfile(LOG_FILE):
        print "Nothing to show"
    else:
        with open(LOG_FILE) as f:
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
        handler = handlers.RotatingFileHandler(filename=LOG_FILE, maxBytes=MB)
    else:
        handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    return handler


def downloader(base_dir, dest_dir, files, username, password, specific=False):
    downloaded = []
    con = Connection(username, password)
    try:
        con.login()
    except WrongLoginException as e:
        print repr(e)
        logger.error(repr(e))
        exit(-1)
    except Exception as e:
        logger.error(repr(e))
    for path, data in files.items():
        try:
            vid_ext = os.path.splitext(path)[1]
            path = os.path.splitext(path)[0]
            sub_file, sub_ext = con.download(path.split("\\")[-1], data)
            logger.info("Found " + path + "!")
            print "Found", path.split("\\")[-1]
            with open(path + sub_ext, "w") as f:
                f.write(sub_file)
            downloaded.append((path, sub_ext, vid_ext))
        except CantFindSubtitleException as e:
            logger.warn(e)
        except Exception as e:
            logger.error(repr(e))
    try:
        con.close(specific)
    except Exception as e:
        logger.error(repr(e))
    if move_finshed(downloaded, base_dir, dest_dir):
        print "\n\nDone! check your Dest folder. you may find surprise\nTry again in a few hours, to prevent the " \
              "chance you'll get ban"
    else:
        print "Done! try again in a few hours, to prevent the chance you'll get ban"


def get_login_credential():
    username = raw_input("Please enter you username (email) for <ktuvit.com>: ")
    password = ""
    while not password:
        password = getpass("Please enter your password: ")
        password1 = getpass("Please enter your password again: ")
        if password != password1:
            print "Can't confirm. let's try again."
            password = ""
    config.add_section("Login")
    config.set("Login", "username", username)
    config.set("Login", "password", base64.b64encode(password))


if __name__ == "__main__":
    main()
