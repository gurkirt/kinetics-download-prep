# Kinetics - Downloader

This repository contains code to download all subsets (700, 600, or 400) of Kinetics dataset.
Code is modified from [ActivityNet Crawler](https://github.com/activitynet/ActivityNet.git).

## What is different
Orignal [Crawler](https://github.com/activitynet/ActivityNet/tree/master/Crawler/Kinetics) store videos in respective label directories. However, there is an overlap among the subsets and labels (class names) are changed, e.g. `passing american football (not in-game)` renamed to `passing American football (not in-game)` from 600 to 700, or class is made more fine-grained, e.g. `picking fruit` into multiple subclasses.
Which leads to multiple duplicate copies of some videos in different subfolder/directories.

Since we have labels in `.csv` files, then we do not need to store videos in respective label directories. 
It provides two benefits, i) avoid same video being stored under different folder, i.e. no duplicate copies ii) directory structure is simple, i.e. all videos are stored under single directory.

## Usage
First, clone this repository and make sure that all the submodules are also cloned properly.

```
git clone git@github.com:gurkirt/kinetics-download-prep.git
cd kinetics-download-prep

```

Next, setup your environment

```
conda install joblib
conda install pandas
conda install sqlite
conda install zlib
conda install -menpo ffmpeg
pip install --upgrade youtube-dl
```

### Re-orgnise existing videos
Use `reorg_kinetics_videos.py` to reorgnise existing videos from `videos_dir`. 

```
python reorg_kinetics_videos.py <videos_dir> <dst_dir>
```

If `dst_dir` doesn't exist the it will create it


### Download videos

Now, you can download the reminaing or all dataset splits by calling:

```
mkdir <output_dir>; python download.py {dataset_split}.csv <output_dir>
```

There is `old_dir` directory name at the start of the script. 
It is to if you want to keep seprate old and new videos. 
While checking for download, we will check if video files already exists in `old_dir` or `output_dir`, if it does then we don't download it. If that is the case then `old_dir` could be `= videos_dir` after re-org.

### Frame dumps

```
python frame_dumps.py <videos_dir> <output_dir> --fps=25 
```

Extract frames at particular frame rate (`--fps=number`) or default (`--fps=0`)

## TODO
### Downscale videos
Smallest side to 256. Skeleton is already there in `downscale_videos.py`.
### Fast loading into Python
Use `python-ffmpeg` to load videos. Trial there in `load_frame_eg.py`, but it doesn't work that fast.

Try alternative ways to load video quick.

Extend it to video chunk loading not the whole video. Should be faster but no easy way to do it other than loading from frame dumps.



