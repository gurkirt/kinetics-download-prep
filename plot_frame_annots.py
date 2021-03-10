import argparse
import os
from collections import OrderedDict
import random
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from PIL import Image
import pdb

def get_video_list(dir):
    new_list = [name for name in os.listdir(dir) if len(name)>2]
    new_list = make_video_name(new_list)
    return new_list


def make_box_anno(llist):
    box = [llist[2], llist[3], llist[4], llist[5]]
    # print(box)
    return [float(b) for b in box]


def read_kinetics_annotations(anno_file):
    lines = open(anno_file, 'r').readlines()
    annotations = {}
    is_train = anno_file.find('train')>-1
    
    for line in lines:
        line = line.rstrip('\n')
        line_list = line.split(',')
        # print(line_list)
        video_name = line_list[0]
        time_stamp = float(line_list[1])
        numf = int(line_list[-1])
        if len(line_list)>2:
            box = make_box_anno(line_list)
            label = int(line_list[6])
            
            if video_name not in annotations:
                annotations[video_name] = [[time_stamp, box, label, numf]]
            else:
                annotations[video_name] += [[time_stamp, box, label, numf]]
        elif not is_train:
            if video_name not in annotations:
                annotations[line_list[0]] = [[time_stamp, None, None, numf]]
            else:
                annotations[line_list[0]] = [[time_stamp, None, None, numf]]

    return annotations



def main(frames_dir, input_csv):
    annotations = read_kinetics_annotations(input_csv)
    for ii, video_name in enumerate(annotations):
        time_stamp = annotations[video_name][0][0]
        src_frames_dir = os.path.join(frames_dir, video_name)
        image_name = os.path.join(src_frames_dir, '{:06d}.jpg'.format(int(time_stamp*30)+1))
        print(video_name, src_frames_dir, image_name)
        img = Image.open(image_name)
        fig, ax = plt.subplots()
        w, h = img.size
        plt.imshow(img)
        print(img.size)
        for anno in  annotations[video_name]:
            box = anno[1] #[x1, y1, x2, y2]
            x1 = int(box[0]*w)
            y1 = int(box[1]*h)
            bw = int((box[2]-box[0])*w)
            bh = int((box[3]-box[1])*h)
            label = anno[2] 
            print(x1,y1, bw, bh)
            rect = patches.Rectangle((x1, y1), bw, bh, linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)
        plt.show(block=False)
        plt.waitforbuttonpress(5)
        plt.close()

if __name__ == '__main__':
    description = 'Helper script for downloading and trimming kinetics videos.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('--frames_dir', default='/home/gusingh/ava-kinetics/frames_x256/', type=str,
                   help='Output directory where videos will be saved.')
    p.add_argument('--input_csv', type=str, default='ava_kinetics_updated_csv/kinetics_train_v1.0.csv',
                   help=('CSV file containing the following format: '
                         'YouTube Identifier,Start time,End time,Class label'))

    args = p.parse_args()
    main(args.frames_dir, args.input_csv)
