# Kinetics - Downloader

This repository contains code to download all subsets (700, 600, or 400) of Kinetics dataset.
Code is modified from [ActivityNet Crawler](https://github.com/activitynet/ActivityNet.git).

## What is different
Orignal [Crawler](https://github.com/activitynet/ActivityNet/tree/master/Crawler/Kinetics) store videos in respective label directories. However, there is an overlap among the subsets and labels (class names) are changed, e.g. `passing american football (not in-game)` renamed to `passing American football (not in-game)` from 600 to 700, or class is made more fine-grained, e.g. `picking fruit` into multiple subclasses.
Which leads copy of same videos in different subfolder/directories.

Since we have labels in `.csv` files, then we do not need to store videos in respective label directories. 
It provides tow benefits, i) avoid same video being stored under different folder, i.e. no duplicate copies of same videos ii) directory structure is simple.

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
pip install --upgrade youtube-dl
```

Finally, download a dataset split by calling:
```
mkdir <data_dir>; python download.py {dataset_split}.csv <data_dir>
