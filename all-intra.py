from os import walk
import json

mypath = "projects/"
_, _, filenames = next(walk(mypath))

all_list = []
for filename in filenames:
    if '-intra.json' in filename:
        dups = json.loads(open(mypath + filename).read())
        all_list += dups

with open('all-intra.json', 'w') as outfile:
    json.dump(all_list, outfile, indent=4)
