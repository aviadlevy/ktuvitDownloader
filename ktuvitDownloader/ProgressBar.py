# -*- coding: utf-8 -*-
"""
The Progress Bar code written by Joey Payne
see here: http://pythoncentral.io/how-to-movecopy-a-file-or-directory-folder-with-a-progress-bar-in-python/
"""
import sys


class ProgressBar(object):
    def __init__(self, message, width=20, progressSymbol='= ', emptySymbol='- '):
        self.width = width

        if self.width < 0:
            self.width = 0

        self.message = message
        self.progressSymbol = progressSymbol
        self.emptySymbol = emptySymbol


    def update(self, progress):
        totalBlocks = self.width
        filledBlocks = int(round(progress / (100 / float(totalBlocks))))
        emptyBlocks = totalBlocks - filledBlocks

        progressBar = self.progressSymbol * filledBlocks + self.emptySymbol * emptyBlocks

        if not self.message:
            self.message = u''

        progressMessage = u'\r{0} {1}  {2}%'.format(self.message, progressBar, progress)

        sys.stdout.write(progressMessage)
        sys.stdout.flush()


    def calculateAndUpdate(self, done, total):
        progress = int(round((done / float(total)) * 100))
        self.update(progress)
