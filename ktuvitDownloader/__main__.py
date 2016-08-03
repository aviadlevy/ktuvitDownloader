import ConfigParser
import base64
import os
from getpass import getpass

from ktuvitDownloader.__version__ import __version__
from ktuvitDownloader.connection import Connection
from ktuvitDownloader.files import getPathsFiles, VIDEO_EXT
from ktuvitDownloader.options import args_parse


CONFIG_FILE = "config.cfg"

config = ConfigParser.RawConfigParser()


def main(args=None):
    """
    main function
    """
    options = args_parse.parse_args()

    if options.version:
        print('+-------------------------------------------------------+')
        print('+               ktuvitDownloader ' + __version__ + (23 - len(__version__)) * ' ' + '+')
        print('+-------------------------------------------------------+')
        print('|      Please report any bug or feature request at      |')
        print('|                 aviadlevy1@gmail.com                  |')
        print('+-------------------------------------------------------+')
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
        dest_dir = raw_input("Enter the path to dest directory (where all your files are): ")
        while not os.path.isdir(dest_dir):
            print "Can't find this directory."
            dest_dir = raw_input("Try again: ")

    if options.reset:
        config.add_section("Directories")
        config.set("Directories", "base_dir", base_dir)
        config.set("Directories", "dest_dir", dest_dir)
        with open(CONFIG_FILE, 'wb') as f:
            config.write(f)

    config.read(CONFIG_FILE)
    username = config.get("Login", "username")
    password = base64.b64decode(config.get("Login", "password"))
    base_dir = config.get("Directories", "base_dir")
    dest_dir = config.get("Directories", "dest_dir")

    files = getPathsFiles(base_dir)
    con = Connection(username, password)
    con.login()
    # for tup_file in files.items():
    #     print val['title']
    con.close()

if __name__ == '__main__':
    main()
