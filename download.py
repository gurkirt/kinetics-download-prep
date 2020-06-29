import argparse
import glob
import json
import os
import shutil
import subprocess
import uuid
import ffmpeg
from collections import OrderedDict

from joblib import delayed
from joblib import Parallel
import pandas as pd

old_dir = ''


def construct_video_filename(row, dirname, trim_format='%06d'):
    """Given a dataset row, this function constructs the
       output filename for a given video.
    """
    basename = '%s_%s_%s.mp4' % (row['video-id'],
                                 trim_format % row['start-time'],
                                 trim_format % row['end-time'])
    output_filename = os.path.join(dirname, basename)

    return output_filename


def download_clip(video_identifier, output_filename,
                  start_time, end_time,
                  num_attempts=5,
                  url_base='https://www.youtube.com/watch?v='):
    """Download a video from youtube if exists and is not blocked.

    arguments:
    ---------
    video_identifier: str
        Unique YouTube video identifier (11 characters)
    output_filename: str
        File path where the video will be stored.
    start_time: float
        Indicates the begining time in seconds from where the video
        will be trimmed.
    end_time: float
        Indicates the ending time in seconds of the trimmed video.

    """
    # Defensive argument checking.
    assert isinstance(video_identifier, str), 'video_identifier must be string'
    assert isinstance(output_filename, str), 'output_filename must be string'
    assert len(video_identifier) == 11, 'video_identifier must have length 11'

    status = False


    # check if file already exists and skip clip
    if os.path.exists(output_filename):
        print("Already Downloaded!")
        return status, 'Downloaded'

    # Construct command line for getting the direct video link.
    # download_clip

    command = ['youtube-dl',
               '--quiet', '--no-warnings',
               '-f', '18',
               '--get-url',
               '"%s"' % (url_base + video_identifier)]
    command = ' '.join(command)
    direct_download_url = None
    # print(command)
    attempts = 0
    while True:
        try:
            direct_download_url = subprocess.check_output(command, shell=True,
                                                          stderr=subprocess.STDOUT)
            direct_download_url = direct_download_url.strip().decode('utf-8')
        except subprocess.CalledProcessError as err:
            attempts += 1
            if attempts == num_attempts:
                return status, err.output
            else:
                continue
        break

    command = ['ffmpeg',
               '-ss', str(start_time),
               '-t', str(end_time - start_time),
               '-i', '"%s"' % direct_download_url,
               '-c:v', 'libx264', '-preset', 'ultrafast',
               '-c:a', 'aac',
               '-threads', '1',
               '-loglevel', 'panic',
               '"%s"' % output_filename]

    command = ' '.join(command)
    try:
        output = subprocess.check_output(command, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        return status, err.output

    status = os.path.exists(output_filename)
    return status, 'Downloaded'


def download_clip_wrapper(row, dirname, trim_format):
    """Wrapper for parallel processing purposes. label_to_dir"""
    output_filename = construct_video_filename(row, dirname, trim_format)
    old_filename = construct_video_filename(row, old_dir, trim_format)
    clip_id = os.path.basename(output_filename).split('.mp4')[0]

    if os.path.exists(output_filename) or os.path.exists(old_filename):
        print('exists', output_filename)
        status = tuple([clip_id, str(True), 'Exists'])
        return status

    downloaded, log = download_clip(row['video-id'], output_filename,
                                    row['start-time'], row['end-time'])
    status = tuple([clip_id, str(downloaded), log])
    return status


def parse_kinetics_annotations(input_csv, ignore_is_cc=False):
    """Returns a parsed DataFrame.

    arguments:
    ---------
    input_csv: str
        Path to CSV file containing the following columns:
          'YouTube Identifier,Start time,End time,Class label'

    returns:
    -------
    dataset: DataFrame
        Pandas with the following columns:
            'video-id', 'start-time', 'end-time', 'label-name'
    """
    df = pd.read_csv(input_csv)
    if 'youtube_id' in df.columns:
        columns = OrderedDict([
            ('youtube_id', 'video-id'),
            ('time_start', 'start-time'),
            ('time_end', 'end-time')])
        df.rename(columns=columns, inplace=True)
        if ignore_is_cc:
            df = df.loc[:, df.columns.tolist()[:-1]]
    return df


def main(input_csv, output_dir,
         trim_format='%06d', num_jobs=24,
         drop_duplicates=False):

    print(input_csv)
    # Reading and parsing Kinetics.
    dataset = parse_kinetics_annotations(input_csv)

    # Download all clips.
    if num_jobs == 1:
        status_lst = []
        for i, row in dataset.iterrows():
            status_lst.append(download_clip_wrapper(
                row, output_dir, trim_format))
    else:
        status_lst = Parallel(n_jobs=num_jobs)(delayed(download_clip_wrapper)(
            row, output_dir, trim_format) for i, row in dataset.iterrows())

    # Clean tmp dir.

    # Save download report.
    # with open('download_report.json', 'w') as fobj:
    #     json.dump( status_lst, fobj)


if __name__ == '__main__':
    description = 'Helper script for downloading and trimming kinetics videos.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('input_csv', type=str,
                   help=('CSV file containing the following format: '
                         'YouTube Identifier,Start time,End time,Class label'))
    p.add_argument('output_dir', type=str,
                   help='Output directory where videos will be saved.')
    p.add_argument('-f', '--trim-format', type=str, default='%06d',
                   help=('This will be the format for the '
                         'filename of trimmed videos: '
                         'videoid_%0xd(start_time)_%0xd(end_time).mp4'))
    p.add_argument('-n', '--num-jobs', type=int, default=24)
    p.add_argument('--drop-duplicates', type=str, default='non-existent',
                   help='Unavailable at the moment')
    # help='CSV file of the previous version of Kinetics.')
    main(**vars(p.parse_args()))
