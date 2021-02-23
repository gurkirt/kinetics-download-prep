
import os, math

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


def main():
    anno_files = ['kinetics_train_v1.0.csv', 'kinetics_val_v1.0.csv', 'kinetics_test_v1.0.csv']
    anno_dir = 'ava_kinetics_csv/'
    new_anno_dir = 'ava_kinetics_updated_csv/'
    trim_format='%06d'
    frames_dir = '/srv/beegfs-benderdata/scratch/da_action/data/ava-kinetics/frames/'
    for anno_name in anno_files:
        anno_file = os.path.join(anno_dir, anno_name)
        annotations = read_kinetics_annotations(anno_file)
        new_csv = open(os.path.join(new_anno_dir, anno_name), 'w')
        total_count = 1
        found_count = 1
        num_frames = 1
        for ii, video in enumerate(annotations):
            for anno in  annotations[video]:
                total_count += 1
                time_stamp = anno[0] 
                video_name = '{:s}_{:s}'.format(video, trim_format % int(math.floor(time_stamp)))
                video_frames_dir = os.path.join(frames_dir, video_name)
                imglist = []
                if os.path.isdir(os.path.join(frames_dir, video_name)):
                    found_count += 1
                    imglist = os.listdir(video_frames_dir)
                    imglist = [img for img in imglist if img.endswith('.jpg')]
                    # if len(imglist)>10:
                    if found_count%1000 == 0:
                        print(ii, video, len(imglist))
                    num_frames += len(imglist)
                #     found_count += 1
                #     integer_time_stamp = int(math.floor(anno[0]))
                #     if integer_time_stamp<= 3:
                #         new_time_stamp = time_stamp
                #     else:
                #         new_time_stamp = 3.0 + time_stamp - integer_time_stamp
                #     wrtie_str = '{:s},{:f},{:d},'.format(video_name, new_time_stamp, len(imglist))
                #     if anno[1] is not None:
                #         for b in anno[1]:
                #             wrtie_str += ',{:f}'.format(b)
                #         wrtie_str += ',{:d}'.format(anno[2])
                #     wrtie_str += '\n'
                #     new_csv.write(wrtie_str)
        new_csv.close()
        print('{:s} found {:d}/{:d} average number of frames {:d}'.format(anno_name, found_count, total_count, int(num_frames/found_count)))


if __name__ == '__main__':
    main()

         

        