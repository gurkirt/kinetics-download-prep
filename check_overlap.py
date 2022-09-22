

import os

base_dir = '/raid/gusingh/datasets/kinetics/k700/'
lists = []
for subset in ['train','val','test']:
    lists.append([v for v in os.listdir('{}Kinetics700-2020-{}/'.format(base_dir, subset)) if len(v)>2])

vcount = 0
for vid in lists[1]:
    if vid in lists[0]:
        vcount += 1

print(vcount)
for vid in lists[2]:
    if vid in lists[0]:
        vcount += 1
print(vcount)