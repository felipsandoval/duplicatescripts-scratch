#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval

import json
from collections import defaultdict, OrderedDict
import string


def main(json_project):
    """
    Find the most frequent blocks among the whole json.
    """
    d = defaultdict(int)
    ordered_words = OrderedDict()
    characters = string.ascii_letters + string.punctuation + string.digits
    characters += "€£ñÑçÇáÁéÉíÍóÓúÚäÄëËïÏöÖüÜàÀèÈìÌò\
                   ÒùÙâÂêÊîÎôÔûÛ¶§©ŠØ®ГДЕЖИЛśĥčýÿў±žПШΘЯбψξλσαβδ"
    # Loops through all sprites
    for sprites_dict in json_project["targets"]:
        for blocks, blocks_value in sprites_dict["blocks"].items():
            try:
                # Counting each opcode from every sprites
                # if "opcode" in blocks_value:
                d[blocks_value['opcode']] += 1
            except TypeError:
                print("Error message: Check this in most_frequent_blocks.py")
                pass
    # Ordering opcodes from least to most frequent
    most_frequent = sorted(d.items(), key=lambda kv: kv[1], reverse=True)
    for block, frequency in most_frequent:
        ordered_words[block] = characters[len(ordered_words)]

    with open('blocks.json', 'w') as outfile:
        json.dump(dict(ordered_words), outfile, indent=4)
