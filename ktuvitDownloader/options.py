#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser


def parse_log(text):
    last_date = text[-1][:10]
    log = [x for x in text if x.startswith(last_date)]
    return "".join(log)


def get_args():
    """
    Builds the argument parser
    :return: the argument parser
    :rtype: ArgumentParser
    """
    opts = ArgumentParser()

    settings_opt = opts.add_argument_group("Settings")
    settings_opt.add_argument("-r", "--reset", dest="reset", action="store_true", default=False,
                              help="Completely reset all the configuration.")
    settings_opt.add_argument("-f", "--change-base-dir", dest="base_path", action="store_true", default=False,
                              help="Change the base dir of your videos.")
    settings_opt.add_argument("-d", "--change-dest-dir", dest="dest_path", action="store_true", default=False,
                              help="Change the base dir of your videos.")
    settings_opt.add_argument("-s", "--specific-location", type=str, dest="specific",
                              help="Download to given file from specific location")
    settings_opt.add_argument("-o", "--organize", action="store_true", default=False, dest="organize",
                              help="Organize your library only")

    information_opts = opts.add_argument_group("Information")
    information_opts.add_argument("-c", "--configuration", dest="show_configuration", action="store_true",
                                  default=False, help="Display configuration.")
    information_opts.add_argument("-v", "--version", dest="show_version", action="store_true", default=False,
                                  help="Display the package version.")
    information_opts.add_argument("-l", "--log", dest="show_log", action="store_true", default=False,
                                  help="Display short log")
    information_opts.add_argument("-la", "--all-log", dest="show_all_log", action="store_true", default=False,
                                  help="Display all log")
    information_opts.add_argument("-ca", "--cache", dest="show_cache", action="store_true", default=False,
                                  help="Display cache")

    return opts


args_parse = get_args()
