
'''

Author: Gurkirt Singh
Start data: 31st August 2019
purpose: of this file is to take all .mp4 videos 
from all the class folder and store them into under single folder

'''
import argparse
import os
import glob
import shutil
import platform


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def main(videos_dir, dst_dir):

    all_files = glob.glob(videos_dir+'**/*')
    all_mp4s = []
    video_names = []

    for file in all_files:
        if file.endswith('.mp4'):
            all_mp4s.append(file)
        else:
            print(file)

    if not os.path.isdir(dst_dir):
        os.makedirs(dst_dir)

    print('total files', len(all_mp4s))
    repition_exists = 0
    for file in all_mp4s:
        videname = file.split('/')[-1]
        dst_file = dst_dir + videname
        if not os.path.isfile(dst_file):
            shutil.move(file, dst_file)
        else:
            time_src = creation_date(file)
            time_dst = creation_date(dst_file)
            repition_exists += 1
            if time_dst >= time_src:  # keep the older files or replace with older file
                shutil.move(file, dst_file)
            else:
                print(file, dst_file)

    print('repitited files', repition_exists)


if __name__ == '__main__':
    description = 'Helper script for re-orgnising kinetics videos'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('videos_dir', type=str,
                   help='Input directory where video exisitng in respective class folders')
    p.add_argument('dst_dir', type=str,
                   help='Output directory where unique videos will be moved')

    main(**vars(p.parse_args()))
