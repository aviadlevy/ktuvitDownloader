#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil

from guessit import guessit

from const import *
from ktuvitDownloader.progress_bar import ProgressBar


def rreplace(s, old, new):
    li = s.rsplit(old, 1)
    return new.join(li)


def get_paths_files(path, to_clean=True):
    """
    return all the files under the path given

    :param path: root folder
    :return: return all the files under the path given
    """
    files = []
    for root, directories, file_names in os.walk(path):
        for filename in file_names:
            files.append(os.path.join(root, filename))
    vid_with_data = {}
    for f in files:
        file_name = os.path.splitext(f)[0]
        for torrent_group in TORRENTS_GROUPS:
            if file_name.lower().endswith(torrent_group.lower()):
                os.rename(f, rreplace(f, torrent_group, ""))
                f = rreplace(f, torrent_group, "")
                break
        ext = os.path.splitext(f)[1]
        size_file = os.path.getsize(f)
        if ext in VIDEO_EXT:
            if size_file < 30 * MB or os.path.splitext(os.path.basename(f))[0] == "sample":
                if to_clean:
                    os.remove(f)
            else:
                data = guessit(f)
                if to_clean:
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
                else:
                    vid_with_data[f] = guessit(f)
        elif ext in SUB_EXT:
            # This is probably mean that this is english sub, so delete
            if to_clean:
                os.remove(f)
        else:
            if size_file < 750 * KB:
                if to_clean:
                    os.remove(f)
    if to_clean:
        clean_empty_dirs(path)
    return vid_with_data


def clear_data_dir(path):
    files = []
    for root, directories, file_names in os.walk(path):
        for filename in file_names:
            files.append(os.path.join(root, filename))
    for f in files:
        ext = os.path.splitext(f)[1]
        if ext == ".zip":
            os.remove(f)


def clean_empty_dirs(path):
    for dir in [x[0] for x in os.walk(path)]:
        if not os.listdir(dir):
            os.rmdir(dir)


def move_finshed(paths, base_dir, dest_dir):
    is_moved = False
    copied = 0
    for path in paths:
        p = ProgressBar("Moving files")
        exts = (path[1], ".srt", ".sub")
        path = path[0]
        folder_name = path.split("\\")[-2]
        file_name = path.split("\\")[-1]
        if not os.path.exists(os.path.join(dest_dir, folder_name)):
            os.makedirs(os.path.join(dest_dir, folder_name))
        for ext in exts:
            try:
                shutil.copy(path + ext, os.path.join(os.path.join(dest_dir, folder_name), file_name) + ext)
                os.remove(path + ext)
            except shutil.Error:
                pass
            except IOError:
                copied -= 1
            copied += 1
            p.calculate_and_update(copied, len(paths) * 2)
            is_moved = True
    clean_empty_dirs(base_dir)
    return is_moved
