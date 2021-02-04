
import os, math
new_dir = 'new_videos'
old_dir = 'old_videos'


def make_video_name(dir_list):
    video_names = {}
    count = 0
    for name in dir_list:
        vname = name[:11]
        # print(name, vname, len(vname))
        # assert(len(vname) ==11), str(len(vname)) + '  '+vname
        time_stamps = [ int(s) for s in name[12:-4].split('_')]
        if name not in video_names:
            video_names[vname] = {'name':name,'timestamps':[time_stamps]}; count +=1
        else:
            video_names[vname]['timestamps'].append(time_stamps)
    # print(count, len(video_names))
    return video_names


def get_video_list(dir):
    new_list = [name for name in os.listdir(dir) if len(name)>2]
    new_list = make_video_name(new_list)
    return new_list


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
    video_file = open(anno_dir+'videos_to_download.csv','w')
    video_file.write('youtube_id,time_start,time_end')
    for anno_name in anno_files:
        anno_file = anno_dir + anno_name
        annotations = read_kinetics_annotations(anno_file)
        for video in annotations:
            for anno in  annotations[video]:
                video_file.write('\n{:s},{:f},{:f}'.format(video, math.floor(anno[0]), -1))

    video_file.close()         
        # print('missing videos [{:d}/{:d}] timestamps found {:d} out of {:d}'.format(pcount, len(annotations), dcount, acount))

if __name__ == '__main__':
    main()

         

        