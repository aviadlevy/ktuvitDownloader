# -*- coding: utf-8 -*-
"""
The Progress Bar code written by Joey Payne
see here: http://pythoncentral.io/how-to-movecopy-a-file-or-directory-folder-with-a-progress-bar-in-python/
"""
import sys


class ProgressBar(object):
    def __init__(self, message, width=20, progress_symbol='= ', empty_symbol='- '):
        self.width = width

        if self.width < 0:
            self.width = 0

        self.message = message
        self.progress_symbol = progress_symbol
        self.empty_symbol = empty_symbol

    def update(self, progress):
        total_blocks = self.width
        filled_blocks = int(round(progress / (100 / float(total_blocks))))
        empty_blocks = total_blocks - filled_blocks

        progress_bar = self.progress_symbol * filled_blocks + self.empty_symbol * empty_blocks

        if not self.message:
            self.message = u''

        progress_message = u'\r{0} {1}  {2}%'.format(self.message, progress_bar, progress)

        sys.stdout.write(progress_message)
        sys.stdout.flush()

    def calculate_and_update(self, done, total):
        progress = int(round((done / float(total)) * 100))
        self.update(progress)
