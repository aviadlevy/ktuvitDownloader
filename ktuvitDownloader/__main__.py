#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import base64
import logging
from logging import handlers
import os
from getpass import getpass

from ktuvitDownloader.CustomExceptions import WrongLoginException, CantFindSubtitleException
from ktuvitDownloader.__version__ import __version__
from ktuvitDownloader.connection import Connection
from ktuvitDownloader.const import *
from ktuvitDownloader.files import get_paths_files, move_finshed
from ktuvitDownloader.options import args_parse

config = ConfigParser.RawConfigParser()

handler = handlers.RotatingFileHandler(filename=LOG_FILE, maxBytes=MB)
handler.setFormatter(logging.Formatter(fmt="%(asctime)s\t%(levelname)s: %(message)s"))

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def main():
    """
    main function
    """
    options = args_parse.parse_args()

    base_dir = ""
    dest_dir = ""

    if options.version:
        print("+-------------------------------------------------------+")
        print("+               ktuvitDownloader " + __version__ + (23 - len(__version__)) * " " + "+")
        print("+-------------------------------------------------------+")
        print("|      Please report any bug or feature request at      |")
        print("| https://github.com/aviadlevy/ktuvitDownloader/issues  |")
        print("+-------------------------------------------------------+")
        exit(1)

    if options.show_log:
        if not os.path.isfile(LOG_FILE):
            print "Nothing to show"
        else:
            with open(LOG_FILE) as f:
                text = f.read()
                if not text:
                    print "Nothing to show"
                else:
                    print text
        exit(1)

    if options.configuration:
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
        exit(1)

    if not os.path.isfile(CONFIG_FILE):
        options.reset = True

    if options.reset:
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
        options.base_path = True
        options.dest_path = True

    if options.base_path:
        base_dir = raw_input("Enter the path to base directory (where all your files are): ")
        while not os.path.isdir(base_dir):
            print "Can't find this directory."
            base_dir = raw_input("Try again: ")

    if options.dest_path:
        dest_dir = raw_input("Enter the path to dest directory (where you want to move your files. it can be the "
                             "same as base): ")
        while not os.path.isdir(dest_dir):
            print "Can't find this directory."
            dest_dir = raw_input("Try again: ")

    if options.reset:
        config.add_section("Directories")
        config.set("Directories", "base_dir", base_dir)
        config.set("Directories", "dest_dir", dest_dir)
        with open(CONFIG_FILE, "wb") as f:
            config.write(f)

    config.read(CONFIG_FILE)
    username = config.get("Login", "username")
    password = base64.b64decode(config.get("Login", "password"))
    base_dir = config.get("Directories", "base_dir")
    dest_dir = config.get("Directories", "dest_dir")

    files = get_paths_files(base_dir)

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
        con.close()
    except Exception as e:
        logger.error(repr(e))

    if move_finshed(downloaded, base_dir, dest_dir):
        print "Done! check your Dest folder. you may find surprise\nTry again in a few hours, to prevent the chance " \
          "you'll get ban"
    else:
        print "Done! try again in a few hours, to prevent the chance you'll get ban"


if __name__ == "__main__":
    main()
