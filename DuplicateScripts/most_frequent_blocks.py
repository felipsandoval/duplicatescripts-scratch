#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Made by Felipe E. Sandoval Sibada

import sys
from os import walk
import json
from collections import defaultdict, OrderedDict
import string

def main (filename):
    d = defaultdict(int)
    ordered_words = OrderedDict()
    ordered_frequency = OrderedDict()

    characters = string.ascii_letters + string.punctuation + string.digits
    characters += "€£ñÑçÇáÁéÉíÍóÓúÚäÄëËïÏöÖüÜàÀèÈìÌòÒùÙâÂêÊîÎôÔûÛ¶§©ŠØ®ГДЕЖИЛśĥčýÿў±žПШΘЯбψξλσαβδ"

    json_project = json.loads(open(filename).read())
    # Loops through all sprites
    for sprites_dict in json_project["targets"]:
        # Gets all blocks out of sprite
        for blocks, blocks_value in sprites_dict["blocks"].items():
            try:
                d[blocks_value['opcode']] += 1
                #Intentar ordenarlos no por número sino por colores y
                #en hexadecimales pej
                #print(d)
            except TypeError:
                print("entre aqui")
                pass
    #print(d.items())
    most_frequent = sorted(d.items(), key=lambda kv: kv[1], reverse=True)
    #print(most_frequent)
    for block, frequency in most_frequent:
        ordered_words[block] = characters[len(ordered_words)]
        #print(ordered_words)

    with open('blocks.json', 'w') as outfile:
        json.dump(dict(ordered_words), outfile, indent=4)

if __name__ == "__main__":
    main(sys.argv[1])
    