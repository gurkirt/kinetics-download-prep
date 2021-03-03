import argparse
import os
import pdb
import numpy as np
import subprocess

from joblib import delayed
from joblib import Parallel


def convert(videoname, video_dir, output_dir):
    video_file = os.path.join(video_dir, videoname)
    downsampled_video_file = os.path.join(output_dir, videoname)
    # downsampled_video_file = '"%s"' % downsampled_video_file
    # video_file = '"%s"' % video_file
    if os.path.exists(downsampled_video_file):
        return 'EXISTS'

    command = 'ffmpeg -y -loglevel panic -i {} -preset ultrafast -filter:v scale="trunc(oh*a/2)*2:256" -threads 1 -max_muxing_queue_size 9999 -c:a copy {}'.format(
        video_file, downsampled_video_file)

    print(command)
    os.system(command)

    try:
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        return err.output

    status = os.path.exists(downsampled_video_file)

    return status


def main(video_dir, output_dir, num_jobs=16):
    print('MAIN')

    videos = os.listdir(video_dir)
    videos = [v for v in videos if v.endswith('.mp4')]

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    videos = sorted(videos)
    # for i, videoname in enumerate(videos):
        # convert(videoname, video_dir, output_dir, fps)
    status_lst = Parallel(n_jobs=num_jobs)(delayed(convert)(videoname, video_dir, output_dir, fps) for i, videoname in enumerate(videos))


if __name__ == '__main__':
    description = 'Helper script for downloading and trimming kinetics videos.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('video_dir', type=str,
                   help='Video directory where videos are saved.')
    p.add_argument('output_dir', type=str,
                   help='Output directory where hf5 db for videos will be saved.')
    p.add_argument('-n', '--num-jobs', type=int, default=16)

    main(**vars(p.parse_args()))


# Stream #0:0(und): Video: h264 (High) (avc1 / 0x31637661), yuv420p, 640x480 [SAR 1:1 DAR 4:3], 638 kb/s, 25 fps, 25 tbr, 12800 tbn, 50 tbc (default)