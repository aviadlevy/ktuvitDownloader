import os
import shutil

from guessit import guessit

from const import *
from ktuvitDownloader.ProgressBar import ProgressBar


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
    for f in files:
        ext = os.path.splitext(f)[1]
        sizefile = os.path.getsize(f)
        if ext in VIDEO_EXT:
            if sizefile < 30 * MB or os.path.splitext(os.path.basename(f))[0] == "sample":
                os.remove(f)
            else:
                data = guessit(f)
                folderName = data["title"]
                if "year" in data.keys():
                    folderName += " - " + str(data["year"])
                newPath = os.path.join(path, folderName)
                try:
                    os.makedirs(newPath)
                except:
                    pass
                shutil.move(f, os.path.join(newPath, f.split("\\")[-1]))
                vid_with_data[os.path.join(newPath, f.split("\\")[-1])] = guessit(f)
        elif ext in SUB_EXT:
            continue
        else:
            if sizefile < 750 * KB:
                os.remove(f)
    cleanEmptyDirs(path)
    return vid_with_data


def cleanEmptyDirs(path):
    for dir in [x[0] for x in os.walk(path)]:
        if not os.listdir(dir):
            os.rmdir(dir)


def moveFinshed(paths, baseDir, destDir):
    isMoved = False
    copied = 0
    for path in paths:
        p = ProgressBar("Moving files")
        exts = (path[1], path[2])
        path = path[0]
        folderName = path.split("\\")[-2]
        fileName = path.split("\\")[-1]
        if not os.path.exists(os.path.join(destDir, folderName)):
            os.makedirs(os.path.join(destDir, folderName))
        for ext in exts:
            shutil.copy(path + ext, os.path.join(os.path.join(destDir, folderName), fileName) + ext)
            os.remove(path + ext)
            copied += 1
            p.calculateAndUpdate(copied, len(paths) * 2)
            isMoved = True
    cleanEmptyDirs(baseDir)
    return isMoved
