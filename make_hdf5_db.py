'''Too expensive don't use it'''

import argparse
import os
import ffmpeg
import pdb
import numpy as np
import h5py
import pickle
# import lmdb
from PIL import Image


def main(video_dir, output_dir, num_jobs=1, fps=25, tmp_dir='/tmp/kinetics/'):
    print('MAIN')
    videos = os.listdir(video_dir)
    videos = [v for v in videos if v.endswith('.mp4')]
    save_file = os.path.join(output_dir, 'greatdb.hdf5')
    print(save_file)
    db = h5py.File(save_file, 'w')
    for k in range(10):
        for vid in videos[:1]:

            video_file = os.path.join(video_dir, vid)
            print(video_file)
            probe = ffmpeg.probe(video_file)
            video_info = next(
                s for s in probe['streams'] if s['codec_type'] == 'video')
            width = int(video_info['width'])
            height = int(video_info['height'])
            print('\n\n dimensions', width, height, '\n\n')
            # num_frames = int(video_info['nb_frames'])
            min_dim = min(height, width)
            scale_format = "{:d}*{:d}".format(int(256 *
                                                  height/min_dim), int(256*width/min_dim))
            (height, width) = int(256*height/min_dim), int(256*width/min_dim)
            out, _ = ffmpeg.input(video_file,).output(
                'pipe:', format='rawvideo', pix_fmt='rgb24', r=fps, s=scale_format).run(capture_stdout=True)

            db[vid+str(k)] = out
            print('shape', video.shape)


if __name__ == '__main__':
    description = 'Helper script for downloading and trimming kinetics videos.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('video_dir', type=str,
                   help='Video directory where videos are saved.')
    p.add_argument('output_dir', type=str,
                   help='Output directory where hf5 db for videos will be saved.')
    p.add_argument('-n', '--num-jobs', type=int, default=1)
    p.add_argument('--fps', type=int, default=25,
                   help='Frame rate at which videos to be extracted')
    p.add_argument('--tmp_dir', type=str, default='/tmp/kinetics/',
                   help='temporary directory where images will be stored for each video')
    main(**vars(p.parse_args()))
