
import os, math
import shutil, argparse

def make_box_anno(llist):
    box = [llist[2], llist[3], llist[4], llist[5]]
    return [float(b) for b in box]


def read_kinetics_annotations(anno_file):
    lines = open(anno_file, 'r').readlines()
    annotations = {}
    is_train = anno_file.find('train')>-1
    
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
        elif not is_train:
            if video_name not in annotations:
                annotations[line_list[0]] = [[time_stamp, None, None]]
            else:
                annotations[line_list[0]] = [[time_stamp, None, None]]

    return annotations

def update_csvs(frames_dir, anno_files, anno_dir):
    new_anno_dir = 'ava_kinetics_updated_csv/'

    if not os.path.isdir(new_anno_dir):
        os.makedirs(new_anno_dir)
    trim_format='%06d'
    frames_dir = args.frames_dir
    for anno_name in anno_files:
        anno_file = os.path.join(anno_dir, anno_name)
        annotations = read_kinetics_annotations(anno_file)
        new_csv = open(os.path.join(new_anno_dir, anno_name), 'w')
        total_count = 1
        found_count = 0
        num_frames = 1
        for ii, video in enumerate(annotations):
            for anno in  annotations[video]:
                total_count += 1
                time_stamp = anno[0] 
                video_name = '{:s}_{:s}'.format(video, trim_format % int(math.floor(time_stamp)))
                video_frames_dir = os.path.join(frames_dir, video_name)
                imglist = []
                if os.path.isdir(os.path.join(frames_dir, video_name)):
                    imglist = os.listdir(video_frames_dir)
                    imglist = [img for img in imglist if img.endswith('.jpg')]
                    num_f= len(imglist)
                    if len(imglist)>120:
                        found_count += 1
                        if found_count%10000 == 0:
                            print(ii, video, len(imglist))
                        num_frames += num_f
                    
                        integer_time_stamp = int(math.floor(anno[0]))
                        if integer_time_stamp<= 3:
                            new_time_stamp = time_stamp
                        else:
                            new_time_stamp = 3.0 + time_stamp - integer_time_stamp
                        wrtie_str = '{:s},{:f},'.format(video_name, new_time_stamp, )
                        if anno[1] is not None:
                            for b in anno[1]:
                                wrtie_str += ',{:f}'.format(b)
                            wrtie_str += ',{:d},{:d}'.format(anno[2],num_f)
                        wrtie_str += '\n'
                        new_csv.write(wrtie_str)
                    else:
                        shutil.rmtree(video_frames_dir)

        new_csv.close()
        
        print('{:s} found {:d}/{:d} average number of frames {:d}'.format(anno_name, found_count, total_count, int(num_frames/found_count)))


def move_dirs(frames_dir, anno_files, anno_dir):

    trim_format='%06d'
    frames_dir = args.frames_dir
    to_move_dir = os.path.join('/'.join(frames_dir.split('/')[:-2]), 'test-frames/')
    print('TO MOVE DIR', to_move_dir)
    if not os.path.isdir(to_move_dir):
        os.makedirs(to_move_dir)
    anno_name = anno_files[-1]
    anno_file = os.path.join(anno_dir, anno_name)
    annotations = read_kinetics_annotations(anno_file)
    total_count = 0
    for ii, video in enumerate(annotations):
        total_count += 1
        time_stamp = annotations[video][0][0]
        video_name = '{:s}_{:s}'.format(video, trim_format % int(math.floor(time_stamp)))
        src_frames_dir = os.path.join(frames_dir, video_name)
        # dst_frames_dir = os.path.join(frames_dir, video_name)
        print(src_frames_dir, to_move_dir)
        if os.path.isdir(src_frames_dir):
            shutil.move(src_frames_dir, to_move_dir)

    print('Moved ', total_count, ' dirs')

    

if __name__ == '__main__':
    description = 'Helper script for updating cvs of ava-kinetics dataset  after video trimming.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('--frames_dir', type=str, default='/raid/susaha/datasets/ava-kinetics/frames_x256/',
                   help='Video directory where videos are saved.')
    args = p.parse_args()
    anno_files = ['kinetics_train_v1.0.csv', 'kinetics_val_v1.0.csv', 'kinetics_test_v1.0.csv']
    anno_dir = 'ava_kinetics_csv/'
    update_csvs(args.frames_dir, anno_files, anno_dir)
    #move_dirs(args.frames_dir, anno_files, anno_dir)

         

        
