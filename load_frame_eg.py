import argparse
import os
import pdb
import numpy as np
import subprocess
import ffmpeg
import time


def main(video_dir):
    print('MAIN')
    t1 = time.time()
    videos = os.listdir(video_dir)
    videos = [v for v in videos if v.endswith('.mp4')]
    for videoname in videos:
        video_file = os.path.join(video_dir, videoname)
        probe = ffmpeg.probe(video_file)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        # print( '\n\n dimensions', width, height, '\n\n')
        out, _ = ffmpeg.input(video_file).output('pipe:', format='rawvideo',  pix_fmt='rgb24', loglevel='panic').run(capture_stdout=True)
        video = np.frombuffer(out,  np.uint8).reshape([-1, height, width, 3])

        print('shape', video.shape)
    print('Time taken', time.time()-t1)

if __name__ == '__main__':
    description = 'Helper script for downloading and trimming kinetics videos.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('video_dir', type=str,
                   help='Video directory where videos are saved.')
   
    main(**vars(p.parse_args()))
