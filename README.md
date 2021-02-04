# Kinetics and AVA-Kinetics - Downloader

This repository contains code to download all subsets (700, 600, or 400) of [Kinetics dataset](https://deepmind.com/research/open-source/kinetics).
You can use the same download code to download 6 seconds long clips around the timestamps provided in [Ava-Kinetics detection dataset](http://research.google.com/ava/).
Code is modified from [ActivityNet Crawler](https://github.com/activitynet/ActivityNet.git).

## Download Kinetics dataset
### What is different from ActivityNet Crawler
Orignal [Crawler](https://github.com/activitynet/ActivityNet/tree/master/Crawler/Kinetics) store videos in respective label directories. However, there is an overlap among the subsets and labels (class names) are changed, e.g. `passing american football (not in-game)` renamed to `passing American football (not in-game)` from 600 to 700, or class is made more fine-grained, e.g. `picking fruit` into multiple subclasses.
Which leads to multiple duplicate copies of some videos in different subfolder/directories.

Since we have labels in `.csv` files, then we do not need to store videos in respective label directories. 
It provides two benefits, i) avoid same video being stored under different folder, i.e. no duplicate copies ii) directory structure is simple, i.e. all videos are stored under single directory.

### Usage
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
conda install -c menpo ffmpeg
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
mkdir <output_dir>; 
```

To download videos from specfic set.

```
python download.py <output_dir> --input_csv={dataset_split}.csv
```

OR, you can download entire dataset with all it's versions and all of it's sets. Just do not sepcify `input_csv`, by default it will pick up `kinetics_csv` directory and all the `.csv` files there.

Also, You can specify number of jobs to run in parllel by `--n=number`. 

```
python download.py <output_dir> 
```

### Frame extraction

```
python frame_extract.py <videos_dir> <output_dir> --fps=30 
```

Extract frames at particular frame rate by `--fps=int_number (default 30)` or video fps via setting `--fps=0`. You can specify number of jobs to run in parllel by `--n=number`. 

### Downscale videos
Smallest side to 256. Skeleton is already there in `downscale_videos.py`.

```
python download.py <input_dir> <output_dir> --fps=30
```

Also, You can specify number of jobs to run in parllel by `--n=number`. 


## Download AVA-Kinetics

Similiar to Kinetics you can download clip around the time stamps provide in AVA-Kinetics dataset.

First step to construction download list from AVA-kinetics annoatated videos and their time stamps. You can run `make_ava_kin_download_csv.py` for it. I have laready performed this task on AVA-kinetics-V.1. And you can find the download csv for AVA-Kinetics in `ava_kinetics_csv`.

Now, similiar to Kinetics, you can run download script.

```
python download.py <output_dir> --input_csv=ava_kinetics_csv\videos_to_download.csv
```

It will download all the clips with `<videoname>_<timestamp>.mp4`. Timestamp here is integer value, calculated from AVA-kinetics timestamps (let's call it `ts`), `timestamp=math.floor(ts)`. Since, we have want a clip around that time stamp, I set the start-time of that clip to be `3` seconds before the `timestamp` and duration to be `6` seconds. To be precise, `start-frame = max(0,timestamp-3)`. When you want to get annotated frame it can be obatined by `frame_number = ts*fps if math.floor(ts)<=3 else (3 + ts-math.floor(ts))*fps` of a video `<videoname>_<timestamp>.mp4` extract at particular `fps`.

## TODO
### Fast loading into Python (under construction)
Use `python-ffmpeg` to load videos. Trial there in `load_frame_eg.py`, but it doesn't work that fast.

Try alternative ways to load video quick.

Extend it to video chunk loading not the whole video. Should be faster but no easy way to do it other than loading from frame dumps.



