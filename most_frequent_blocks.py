import sys
from os import walk
import json
from collections import defaultdict, OrderedDict
import string

d = defaultdict(int)
ordered = OrderedDict()

characters = string.ascii_letters + string.punctuation + string.digits
characters += "€£ñÑçÇáÁéÉíÍóÓúÚäÄëËïÏöÖüÜàÀèÈìÌòÒùÙâÂêÊîÎôÔûÛ¶§©ŠØ®ГДЕЖИЛśĥčýÿў±žПШΘЯбψξλσαβδ"

mypath = sys.argv[1]
_, _, filenames = next(walk(mypath))
for filename in filenames:
    json_project = json.loads(open(mypath + filename).read())

    # Loops through all sprites
    for sprites_dict in json_project["targets"]:
        sprite = sprites_dict["name"]

        # Gets all blocks out of sprite
        for blocks, blocks_value in sprites_dict["blocks"].items():
            try:
                d[blocks_value['opcode']] += 1
            except TypeError:
                pass

most_frequent = sorted(d.items(), key=lambda kv: kv[1], reverse=True)
for block, frequency in most_frequent:
    ordered[block] = characters[len(ordered)]

with open('blocks.json', 'w') as outfile:
    json.dump(dict(ordered), outfile, indent=4)