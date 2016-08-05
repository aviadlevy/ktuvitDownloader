import os

from guessit import guessit

from const import *


def getPathsFiles(path):
    """
    return all the files under the path given

    :param path: root folder
    :return: return all the files under the path given
    """
    files = []
    for root, directories, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    vid_with_data = {}
    for file in files:
        ext = os.path.splitext(file)[1]
        sizefile = os.path.getsize(file)
        if ext in VIDEO_EXT:
            if sizefile < 30 * MB or os.path.splitext(os.path.basename(file))[0] == "sample":
                os.remove(file)
            else:
                vid_with_data[file] = guessit(file)
        elif ext == "srt":
            continue
        else:
            if sizefile < 750 * KB:
                os.remove(file)
    return vid_with_data
