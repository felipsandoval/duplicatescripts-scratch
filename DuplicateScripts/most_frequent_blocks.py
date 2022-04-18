#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from os import walk
import json
from collections import defaultdict, OrderedDict
import string

def main (json_project):
    d = defaultdict(int)
    ordered_words = OrderedDict()

    characters = string.ascii_letters + string.punctuation + string.digits
    characters += "€£ñÑçÇáÁéÉíÍóÓúÚäÄëËïÏöÖüÜàÀèÈìÌòÒùÙâÂêÊîÎôÔûÛ¶§©ŠØ®ГДЕЖИЛśĥčýÿў±žПШΘЯбψξλσαβδ"

    #json_project = json.loads(open(filename).read())
    print("\n")
    print(json_project)
    print("\n")
    # Loops through all sprites
    for sprites_dict in json_project["targets"]:
        # Gets all blocks out of sprite
        for blocks, blocks_value in sprites_dict["blocks"].items():
            try:
                d[blocks_value['opcode']] += 1
            except TypeError:
                print("entre aqui")
                pass
    most_frequent = sorted(d.items(), key=lambda kv: kv[1], reverse=True)
    for block, frequency in most_frequent:
        ordered_words[block] = characters[len(ordered_words)]

    with open('blocks.json', 'w') as outfile:
        json.dump(dict(ordered_words), outfile, indent=4)

#if __name__ == "__main__":
#    main(sys.argv[1])
    