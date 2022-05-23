#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval

import sys
from os import walk
import json
from collections import defaultdict, OrderedDict
import string

def main (json_project):
    """
    Find the most frequent blocks among the duplicate blocks.
    """
    d = defaultdict(int)
    ordered_words = OrderedDict()

    characters = string.ascii_letters + string.punctuation + string.digits
    characters += "€£ñÑçÇáÁéÉíÍóÓúÚäÄëËïÏöÖüÜàÀèÈìÌòÒùÙâÂêÊîÎôÔûÛ¶§©ŠØ®ГДЕЖИЛśĥčýÿў±žПШΘЯбψξλσαβδ"

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
                print("Hay un error ?¿ check this")
                pass
    most_frequent = sorted(d.items(), key=lambda kv: kv[1], reverse=True)
    for block, frequency in most_frequent:
        ordered_words[block] = characters[len(ordered_words)]

    with open('blocks.json', 'w') as outfile:
        json.dump(dict(ordered_words), outfile, indent=4)