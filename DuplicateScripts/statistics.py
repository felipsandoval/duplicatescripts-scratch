#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval

from collections import Counter, defaultdict
import json
import string


def json2dna(filename):
    """
    Given a JSON file as given in duplicateScriptsApprox.py
    returns the scripts as characters
    """
    scripts = []
    blocks_dict = json.loads(open('blocks.json').read())  # block -> char
    characters = string.ascii_letters + string.punctuation + string.digits
    characters += "€£ñÑçÇáÁéÉíÍóÓúÚäÄëËïÏöÖüÜàÀèÈìÌòÒùÙâÂêÊîÎôÔûÛ¶§©ŠØ®ГДЕЖИЛśĥčýÿў±žПШΘЯбψξλσαβδ"
    #duplicates = json.loads(open(filename).read())
    duplicates = filename
    if not duplicates:
        return (None, None)
    for script in duplicates:
        block_list = []
        for block in script:
            if block not in blocks_dict:
                blocks_dict[block] = characters[len(blocks_dict)]  # Para asignar uno nuevo con su nueva letra
            block_list.append(blocks_dict[block])
        scripts.append(''.join(block_list))
    return(scripts, blocks_dict)


def main(filename):
    (scripts, blocks_dict) = json2dna(filename)
    if not blocks_dict:
        return None
    inv_blocks_dict = {v: k for k, v in blocks_dict.items()}
    c = Counter(tuple(scripts))
    # print(c)
    most_common = c.most_common(10)
    print("10 most common:")
    for most in most_common:
        print(most[1], "times")
        for char in most[0]:
            print("  ", inv_blocks_dict[char])
    print()
    print("Different blocks:", len(list(c)))
