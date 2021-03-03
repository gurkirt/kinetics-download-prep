import argparse
import glob
import json
import os
import shutil
import subprocess
import uuid
import os
from collections import OrderedDict
from pathlib import Path
from joblib import delayed
from joblib import Parallel
import pandas as pd
import random
old_dir = '../videos_old/'


def construct_video_filename(row, dirname, trim_format='%06d'):
    """Given a dataset row, this function constructs the
       output filename for a given video.
    """
    
    # print('HHHHHEEEERRRRREEEE', row, dirname)
    if row['end-time']>0:
        basename = '%s_%s_%s.mp4' % (row['video-id'],
                                 trim_format % row['start-time'],
                                 trim_format % row['end-time'])
    else:
        basename = '%s_%s.mp4' % (row['video-id'], trim_format % row['start-time'])
    
    output_filename = os.path.join(dirname, basename)
    return output_filename


def download_clip(video_identifier, output_filename,
                  start_time, end_time,
                  num_attempts=3,
                  tmp_dir='/tmp/kinetics/',
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

    if not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir)
    # check if file already exists and skip clip
    if check_if_video_exist(output_filename):
        print("Already Downloaded!")
        return status, 'Downloaded'

    # Construct command line for getting the direct video link.
    # download_clip
    #print('We are downloading to', output_filename) 

    # tmp_filename = os.path.join(tmp_dir, '%s.%%(ext)s' % uuid.uuid4())
    command = ['youtube-dl',
               #'--quiet', '--no-warnings',
               '-f', 'mp4',
            #    '-o', '"%s"' % tmp_filename,
               '--get-url',
               '"%s"' % (url_base + video_identifier)]
    command1 = ' '.join(command)
    
    attempts = 0
    #print('attempting to download', command1)
    while True:
        try:
            #os.system(command1)
            direct_download_url = subprocess.check_output(command1, shell=True,
                                             stderr=subprocess.STDOUT)
            direct_download_url = direct_download_url.strip().decode('utf-8')
        except subprocess.CalledProcessError as err:
            attempts += 1
            if attempts == num_attempts:
                return status, err.output
            else:
                continue
        break
    
    # tmp_filename = glob.glob('%s*' % tmp_filename.split('.')[0])[0]
    #print('downloaded 2', tmp_filename)
    if end_time>0:
        command = ['ffmpeg',
                '-ss', str(start_time),
                '-t', str(end_time - start_time),
                # '-i', '"%s"' % tmp_filename,
                '-i', '"%s"' % direct_download_url,
                '-c:v', 'libx264', 
                '-c:a', 'copy',
                '-threads', '1',
                '-loglevel', 'panic',
                '"%s"' % output_filename]
    else:
        # print( output_filename, start_time, end_time)
        command = ['ffmpeg -y',
                    '-ss', str(max(0, start_time-3)),
                    '-t', str(6),
                    # '-i', '"%s"' % tmp_filename,
                    '-i', '"%s"' % direct_download_url,
                    # '-c:v', 'libx264', 
                    '-c:a', 'copy',
                    '-threads', '1',
                    '-max_muxing_queue_size', '9999',
                    '-loglevel', 'panic',
                    '"%s"' % output_filename]

    command = ' '.join(command)
    print(command1, command)
    try:
        output = subprocess.check_output(command, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        return status, err.output

    status = os.path.exists(output_filename)
    os.remove(tmp_filename)
    return status, 'Downloaded'


def download_clip_wrapper(row, output_filename):
    """Wrapper for parallel processing purposes. label_to_dir"""
    
    #print(row, type(row))
    #print(output_filename)
    downloaded, log = download_clip(row['video-id'], output_filename, row['start-time'], row['end-time'])
    status = tuple([str(downloaded), output_filename, log])

    return status

def get_csv_df(input_csv):
    df = pd.read_csv(input_csv)
    if 'youtube_id' in df.columns:
        columns = OrderedDict([
            ('youtube_id', 'video-id'),
            ('time_start', 'start-time'),
            ('time_end', 'end-time')])
        df.rename(columns=columns, inplace=True)
    return df


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
    if input_csv.endswith('.csv'):
        df = get_csv_df(input_csv)
    else:
        input_csv_dir = input_csv
        csv_list = os.listdir(input_csv)
        csv_list = [f for f in csv_list if f.endswith('.csv')]
        # print(csv_list)
        df = None
        for f in csv_list:
            cdf = get_csv_df(os.path.join(input_csv_dir,f))
            print('Loaded ', f, 'for',len(cdf), 'items')
            if df is None:
                df = cdf
            else:
                df = df.append(cdf, sort=True)
    df = df.drop_duplicates()
    assert df is not None, df

    return df


def check_if_video_exist(output_filename):

    if os.path.exists(output_filename):
        # print(get_output_filename, 'exists ')
        fsize = Path(output_filename).stat().st_size
        # print('exists', output_filename, 'with file size of ',fsize, ' bytes')
        if fsize>10:
            return  True
        else:
            os.remove(output_filename)
            print('CHECK file size of ',fsize, ' bytes', output_filename)
    return False


def get_output_filename(row, dirname, trim_format):
    output_filename = construct_video_filename(row, dirname, trim_format)
    # old_filename = construct_video_filename(row, old_dir, trim_format)
    # clip_id = os.path.basename(output_filename).split('.mp4')[0]

        
    return output_filename, check_if_video_exist(output_filename)

def make_video_names(dataset, output_dir, trim_format):
    video_name_list = {}
    row_list = []
    count_done = 0
    total = len(dataset)
    print('Total is ', total)
    for ii, row in dataset.iterrows():
        if ii>1099999999999999:
            break
            
        output_filename, done = get_output_filename(row, output_dir, trim_format)
        if not done and output_filename not in video_name_list:
            video_name_list[output_filename] = 1
            row_list.append([row, output_filename])
        elif output_filename not in video_name_list:
            video_name_list[output_filename] = 0
            count_done += 1
    video_name_list = [v for v in video_name_list]
    video_name_set = list(set(video_name_list))
    
    print('Done {:d} out of {:d} dict count {:d} set count {:d}'.format(count_done, total, len(video_name_list), len(video_name_set)))

    return row_list


def main(input_csv, output_dir,
         trim_format='%06d', num_jobs=24,
         drop_duplicates=False):

    print(input_csv, output_dir)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    # Reading and parsing Kinetics.
    dataset = parse_kinetics_annotations(input_csv)
    video_names = make_video_names(dataset, output_dir, trim_format)
    print('NUMBER OF VIDEOS TO BE DOWNLOADED', len(video_names))
    # Download all clips.

    if num_jobs <= 1:
        status_lst = []
        for _, row in enumerate(video_names):
            status_lst.append(download_clip_wrapper(row[0], row[1]))
    else:
        status_lst = Parallel(n_jobs=num_jobs)(delayed(download_clip_wrapper)(row[0], row[1]) for row in video_names)

    # Clean tmp dir.
    # Save download report.
    # with open('download_report.json', 'w') as fobj:
    #     json.dump( status_lst, fobj)

if __name__ == '__main__':
    description = 'Helper script for downloading and trimming kinetics videos.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('output_dir', type=str,
                   help='Output directory where videos will be saved.')
    p.add_argument('--input_csv', type=str, default='kinetics_csv/',
                   help=('CSV file containing the following format: '
                         'YouTube Identifier,Start time,End time,Class label'))
    p.add_argument('-f', '--trim-format', type=str, default='%06d',
                   help=('This will be the format for the '
                         'filename of trimmed videos: '
                         'videoid_%0xd(start_time)_%0xd(end_time).mp4'))
    p.add_argument('-n', '--num-jobs', type=int, default=20)
    p.add_argument('--drop-duplicates', type=str, default='non-existent',
                   help='Unavailable at the moment')
    main(**vars(p.parse_args()))
