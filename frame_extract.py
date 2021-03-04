import argparse
import os
import pdb
import numpy as np
import subprocess

from joblib import delayed
from joblib import Parallel


def extract(videoname, video_dir, output_dir, fps):
    video_file = os.path.join(video_dir, videoname)
    frames_dir = os.path.join(output_dir, videoname[:-4])

    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)

    imglist = os.listdir(frames_dir)
    imglist = [img for img in imglist if img.endswith('.jpg')]

    if len(imglist) < 180:  # very few or no frames try extracting againg
        if fps > 0:
            command = 'ffmpeg -loglevel panic -threads 1 -max_muxing_queue_size 9999 -i {} -q:v 2 -r {} {}/%06d.jpg'.format(video_file, fps, frames_dir)
        else:
            command = 'ffmpeg -loglevel panic -threads 1 -max_muxing_queue_size 9999 -i {} -q:v 2 {}/%06d.jpg'.format(video_file, frames_dir)

        try:
            output = subprocess.check_output(
                command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            return err.output

    imglist = os.listdir(frames_dir)
    imglist = [img for img in imglist if img.endswith('.jpg')]

    return len(imglist)


def main(video_dir, output_dir, num_jobs=16, fps=30):
    print('MAIN')

    videos = os.listdir(video_dir)
    videos = [v for v in videos if v.endswith('.mp4')]

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    videos = sorted(videos)
    # for i, videoname in enumerate(reversed(videos)):
    #     numf = extract(videoname, video_dir, output_dir, fps)
        # extract(videoname, video_dir, output_dir, fps)
    status_lst = Parallel(n_jobs=num_jobs)(delayed(extract)(videoname, video_dir, output_dir, fps) for i, videoname in enumerate(videos[:16]))


if __name__ == '__main__':
    description = 'Helper script for downloading and trimming kinetics videos.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('video_dir', type=str,
                   help='Video directory where videos are saved.')
    p.add_argument('output_dir', type=str,
                   help='Output directory where hf5 db for videos will be saved.')
    p.add_argument('-n', '--num-jobs', type=int, default=16)
    p.add_argument('--fps', type=int, default=30,
                   help='Frame rate at which videos to be extracted')

    main(**vars(p.parse_args()))
