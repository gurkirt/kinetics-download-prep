

import os, math
import shutil, argparse
from collections import OrderedDict
import pandas as pd

def make_box_anno(llist):
    box = [llist[2], llist[3], llist[4], llist[5]]
    return [float(b) for b in box]

def read_kinetics_annotations(anno_file):
    lines = open(anno_file, 'r').readlines()
    annotations = {}
    is_test = anno_file.find('test')>-1
    
    for line in lines:
        line = line.rstrip('\n')
        line_list = line.split(',')
        video_name = line_list[0]
        time_stamp = float(line_list[1])
        if len(line_list)>2:
            box = make_box_anno(line_list)
            label = int(line_list[-1])
            if video_name not in annotations:
                annotations[video_name] = [[time_stamp, box, label]]
            else:
                annotations[video_name] += [[time_stamp, box, label]]
        else:
            if video_name not in annotations:
                annotations[line_list[0]] = [[time_stamp, None, None]]
            else:
                annotations[line_list[0]] = [[time_stamp, None, None]]

    return annotations


def parse_video_list(args):
    print('Loading video list from ', args.video_dir)
    video_list = [v for v in os.listdir(args.video_dir) if len(v)>0]
    print('Total number of videos are ', len(video_list))
    videos = {}
    for vid in video_list:
        vidname, ext = vid.split('.')[0], vid.split('.')[1]
        if ext != 'mp4':
            print('We have problem video ext', vid, ext)
        video_name, vidname = vidname[:11], vidname[11:] 
        _, start_time, end_time = vidname.split('_')
        assert len(video_name) == 11, '{} {} has length of {}'.format(vid, video_name, len(video_name))
        if video_name in videos:
            videos[video_name].append([vid, start_time, end_time])
        else:
            videos[video_name] = [[vid, start_time, end_time]]


    return videos


def get_kinetics700_video_bounds(videos, video, time_stamp):
    timelines = videos[video]
    best_id = 0
    best_middiff = 100000
    for idx, (vid, st, et) in enumerate(timelines):
        st, et  = float(st), float(et)
        # if st < time_stamp and et > time_stamp:
        midpoint = (st+et)/2.0 - st
        # print(midpoint)
        middiff = abs((st+et)/2.0 - time_stamp)
        if middiff<best_middiff:
            best_id = idx
            best_middiff = middiff
    
    vid, st, et = timelines[best_id]
    return vid, float(st), float(et), best_middiff

def remove_unsed(args, subsets, anno_dir):
    new_anno_dir = 'ava_kinetics_700_updated_csv/'
    videos = parse_video_list(args)
    
    vide_present = {}

    for subset in subsets:
        anno_file = os.path.join(anno_dir, 'kinetics_{}_v1.0.csv'.format(subset))    
        annotations = read_kinetics_annotations(anno_file)
        for ii, video in enumerate(annotations):
                if video in videos:
                    vide_present[video] = True
        print("subset: ", subset, ' present are', len(vide_present))
    
    tokeep = 0
    todelete = 0
    for video in videos:
        timelines = videos[video]
        for idx, (vid, st, et) in enumerate(timelines):
            video_path = os.path.join(args.video_dir, vid)
            # print(video_path)
            if video in vide_present:
                tokeep += 1
            else:
                todelete += 1
                os.remove(video_path)


    print('Tokeep', tokeep, 'to delete', todelete)



def update_csvs(args, subsets, anno_dir):
    new_anno_dir = 'ava_kinetics_700_updated_csv/'
    videos = parse_video_list(args)
    
    if not os.path.isdir(new_anno_dir):
        os.makedirs(new_anno_dir)
    trim_format='%06d'
    bad_count = {}
    miss_count = {}
    dduration = 0
    dcount = 0
    less_125 = 0
    tt = 0
    for subset in subsets:
        anno_file = os.path.join(anno_dir, 'kinetics_{}_v1.0.csv'.format(subset))
        frames_dir = args.frames_dir + subset
        annotations = read_kinetics_annotations(anno_file)
        # print('Update ', len(annotations), 'annotations videos')
        new_csv = open(os.path.join(new_anno_dir, 'kinetics_{}_v1.0.csv'.format(subset)), 'w')
        total_count = {}
        found_count = 0
        num_frames = 1
        for ii, video in enumerate(annotations):
            
            for time_stamp, box, label in annotations[video]:
                # time_stamp = annotations[video][0][0]
                ts_name = video+'_{:06d}'.format(int(time_stamp))
                total_count[ts_name] = 1
                if video not in videos:
                    # print(video+ ' not in kinetic 700 videos') 
                    if ts_name not in miss_count:
                        miss_count[ts_name] = 1
                    continue
                
                video_file_name, vst, et, best_val = get_kinetics700_video_bounds(videos, video, time_stamp)
                if best_val>4.0:
                    if ts_name not in bad_count:
                        bad_count[ts_name] = 1
                    continue

                tt += 1
                
                reltive_time_stamp = time_stamp-vst
                assert reltive_time_stamp > 0.9
                assert reltive_time_stamp < 9.1
                if reltive_time_stamp>1.25:
                    new_time_stamp = 1.25
                    start_time = reltive_time_stamp - new_time_stamp
                    duration = min(2.5, 1.25+10-reltive_time_stamp)
                else:
                    new_time_stamp = reltive_time_stamp
                    start_time = reltive_time_stamp - new_time_stamp
                    duration = min(2.5,1.25+10-reltive_time_stamp)
                    less_125 += 1
                
                # if reltive_time_stamp>8.9:
                #     print(video, video_name, vst, time_stamp, duration, new_time_stamp, st)
                
                dduration += duration
                dcount += 1
                # print(vst,time_stamp)
                new_video_name = '{}_{:02d}_{:02d}_{:04d}'.format(video,int(vst),int(time_stamp),int(new_time_stamp*100))
                video_frames_dir = os.path.join(frames_dir, new_video_name)
                if not os.path.isdir(video_frames_dir):
                    os.makedirs(video_frames_dir)
                
                input_file = os.path.join(args.video_dir, video_file_name)

                cmd = 'ffmpeg -i {:s} -r 30 -q:v 1 -ss {:0.5f} -t {:0.5f} -threads 1 -filter:v "scale=if(lte(iw\,ih)\,min(256\,iw)\,-2):if(gt(iw\,ih)\,min(256\,ih)\,-2)" {:s}/%06d.jpg'.format(input_file, start_time, duration, video_frames_dir)
                print(cmd)
                os.system(cmd)
            #     break
            # break

        #         imglist = []
        #         if os.path.isdir(os.path.join(frames_dir, video_name)):
        #             imglist = os.listdir(video_frames_dir)
        #             imglist = [img for img in imglist if img.endswith('.jpg')]
        #             num_f= len(imglist)
        #             min_frames = int(new_time_stamp*30+20)
        #             if len(imglist)>=min_frames:
        #                 found_count += 1
        #                 if found_count%10000 == 0:
        #                     print(ii, video, len(imglist))
        #                 num_frames += num_f
 
        #                 wrtie_str = '{:s},{:f}'.format(video_name, new_time_stamp, )
        #                 if anno[1] is not None:
        #                     for b in anno[1]:
        #                         wrtie_str += ',{:f}'.format(b)
        #                     wrtie_str += ',{:d},{:d}'.format(anno[2],num_f)
        #                 wrtie_str += '\n'
        #                 new_csv.write(wrtie_str)
        #             else:
        #                 shutil.rmtree(video_frames_dir)
        # new_csv.close()

        print(' Subset: {}: bad count is:: {} Missing videos are {} Totol time stamps {}'.format(subset, len(bad_count), len(miss_count), len(total_count)))
        print('Avg duration {} less than1.25 {}'.format(dduration/dcount, less_125/tt))

        # print('Missing videos are ', len(miss_count), subset)
        # print('Total time stamps ', len(total_count))
        # print('Number of time stamps with problem', len(miss_count)+len(bad_count))
        # count = 0
        
        # keys = [v for v in bad_count]
        
        # keys = keys + [ v for v in miss_count if v not in keys]
        
        # for vid in keys:
        #     images_dir = '/raid/susaha/datasets/ava-kinetics/images/'+vid
        #     if os.path.isdir(images_dir):
        #         imglist = [im for im in os.listdir(images_dir) if im.endswith('.jpg')]
        #         if len(imglist)>120:
        #             count += 1
        
        # print('found are ', count)
        # print('{:s} found {:d}/{:d} average number of frames {:d}'.format(anno_name, found_count, total_count, int(num_frames/found_count)))

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


def get_csv_df(input_csv):
    df = pd.read_csv(input_csv)
    if 'youtube_id' in df.columns:
        columns = OrderedDict([
            ('youtube_id', 'video-id'),
            ('time_start', 'start-time'),
            ('time_end', 'end-time')])
        df.rename(columns=columns, inplace=True)
    return df


def check_avakin_valset_overlap(args, subsets, anno_dir):
    avakin_val = '/raid/susaha/datasets/ava-kinetics/annotations/ava_val.csv'
    avakin_val = read_kinetics_annotations(avakin_val)

    for subset in ['700_2020', '600']:
        kin_csv = 'kinetics_csv/kinetics-{}_train.csv'.format(subset)    
        kin_videos = parse_kinetics_annotations(kin_csv)
        kin_video_names = {}
        for ii, row in kin_videos.iterrows():
            kin_video_names[row['video-id']] = 1
        
        print(kin_videos[:10])
        avakin_vidoes = [v for v in avakin_val]
        cc = 0
        for vid in avakin_vidoes:
            if vid in kin_video_names:
                cc += 1
        print(subset, ' has overlap with avakin val set of ', cc)

    


if __name__ == '__main__':
    description = 'Helper script for updating cvs of kinetics dataset  after video trimming.'
    p = argparse.ArgumentParser(description=description)
    # p.add_argument('--video_dir', type=str, default='/srv/beegfs-benderdata/scratch/da_action/data/kinetics700_cvdf/videos/train/',
    #                help='Video directory where videos are saved.')
    
    p.add_argument('--video_dir', type=str, default='/raid/gusingh/datasets/kinetics/k700_videos/',
                   help='Video directory where videos are saved.')
    p.add_argument('--frames_dir', type=str, default='/raid/gusingh/datasets/kinetics/kinetics_det_frames/',
                   help='Video directory where videos are saved.')
    args = p.parse_args()
    # anno_files = ['kinetics_train_v1.0.csv', 'kinetics_val_v1.0.csv', 'kinetics_test_v1.0.csv']
    subsets = ['train','val','test']
    
    anno_dir = 'ava_kinetics_csv/'
    # remove_unsed(args, subsets, anno_dir)
    # anno_dir = '/raid/susaha/datasets/ava-kinetics/kinetics/annotations/'
    subsets = ['train']
    update_csvs(args, subsets, anno_dir)
    # check_avakin_valset_overlap(args, subsets, anno_dir)

         

        
