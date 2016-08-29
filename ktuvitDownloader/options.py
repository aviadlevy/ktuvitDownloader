#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser


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

    information_opts = opts.add_argument_group("Information")
    information_opts.add_argument("-c", "--configuration", dest="configuration", action="store_true", default=False,
                                  help="Display configuration.")
    information_opts.add_argument("-v", "--version", dest="version", action="store_true", default=False,
                                  help="Display the package version.")
    information_opts.add_argument("-l", "--log", dest="show_log", action="store_true", default=False,
                                  help="Display log")

    return opts


args_parse = get_args()
