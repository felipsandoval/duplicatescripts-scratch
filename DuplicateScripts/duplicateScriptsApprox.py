#!/usr/bin/python3
# -*- coding: utf-8 -*-

from difflib import SequenceMatcher
import json
import zipfile
import sys
import shutil
from more_itertools import flatten

N_BLOCKS = 6
LOOP_BLOCKS = ["control_repeat", "control_forever", "control_if",
               "control_if_else", "control_repeat_until"]


def find_dups(blocks):
    """
    Given blocks, which is a list of sequences of blocks
    Returns those subsequences that are duplicated
    """
    return_list = []
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            #print(blocks[i], blocks[j])
            s = SequenceMatcher(None, blocks[i], blocks[j]) 
            #print(s.ratio()*100)
            match = s.find_longest_match(0, len(blocks[i]), 0, len(blocks[j]))
            #print(match.size)
            if match.size >= N_BLOCKS:
                return_list.append(blocks[i][match.a:match.a + match.size])
    return return_list

def blocks2ignore():
    """
    Open .TXT and parser the blocks opcodes that are going to be ignored
    as duplicated scripts
    """
    with open('IgnoreBlocks.txt') as f:
        ignore_list = f.read().splitlines()
    f.close
    return ignore_list

def sb3_json_extraction(fileIn):
    """
    Will change the file extention to .zip from a given a .sb3,
    then will return the .json file inside the Scratch project.
    """
    fileOut = fileIn.split(".")[0] + ".zip"
    shutil.copyfile(fileIn, fileOut)
    zip_file = zipfile.ZipFile(fileOut, "r")
    listOfFileNames = zip_file.namelist()
    # Iterates over the file names to find .json
    for fileName in listOfFileNames:
        if fileName.endswith('.json'):
            json_file = zip_file.extract(fileName)
    json_project = json.loads(open(json_file).read())
    os.remove(fileOut)
    return json_project

def obtaining_json(filename):
    """Obtains JSON"""
    try:
        if filename.endswith(".zip"):
            zip_file = zipfile.ZipFile(filename, "r")
            # Aquí hay que hacer el caso en el que sean VARIOS archivos JSON.
            json_file = json.loads(zip_file.open("project.json").read())
        elif filename.endswith(".json"):
            json_file = json.loads(open(filename).read())
        elif filename.endswith(".sb3"):
            json_file = sb3_json_extraction(filename)
    except:
        sys.exit("\nPlease, use a valid extension file like .SB3," +
        " JSON or .ZIP\n")
    return json_file

class DuplicateScripts():
    """
    Analyzer of duplicate scripts in sb3 projects
    New version for Scratch 3.0
    """

    def __init__(self, ignoring):
        self.ignoringisactive = ignoring
        self.toplevel_list = []

    def analyze(self, filename):
        """Start parsering it"""
        json_project = obtaining_json(filename)
        scripts_dict = {}
        ignoreblock_list = blocks2ignore()

        # Loops through all sprites (and canva "sprite" too)
        for sprites_dict in json_project["targets"]:
            sprite = sprites_dict["name"]
            blocks_dict = {}
            scripts_dict[sprite] = []
            # Gets all blocks out of sprite
            for blocks, blocks_value in sprites_dict["blocks"].items():
                if isinstance(blocks_value, dict):
                    blocks_dict[blocks] = blocks_value


            opcode_dict = {}   # block id -> block opcode
            tmp_blocks = []
            order_loop = []
            tmp_blocks2 = []
            opcode_list_ord = []
            loop_list = []
            loop_list2 = []
            loops_dict = {}
            loops_dict2 = {}


            for block_id, block in blocks_dict.items():
                opcode_dict[block_id] = block["opcode"]
                if block["opcode"] in LOOP_BLOCKS:
                    #loop_list = getloopb(block, blocks_dict)
                    #loops_dict[block["parent"]] = loop_list
                    loop_list2 = getloop_ids(block, blocks_dict)
                    loops_dict2[block["parent"]] = loop_list2
                    #print(loops_dict)
                    #print(loops_dict2)
                if self.ignoringisactive and block["opcode"] not in ignoreblock_list:
                    if block["topLevel"]:
                        if tmp_blocks:
                            scripts_dict[sprite].append(tmp_blocks)
                        tmp_blocks = [block["opcode"]]
                    else:
                        tmp_blocks.append(block["opcode"])
                elif self.ignoringisactive:
                    print("IGNORO BLOQUE")
                else:
                    if block["topLevel"]:
                        if tmp_blocks:
                            scripts_dict[sprite].append(tmp_blocks)
                        tmp_blocks = [block["opcode"]]
                        opcode_list_ord = [block_id]
                    else:
                        tmp_blocks.append(block["opcode"])
                        opcode_list_ord.append(block_id)
            opcode_list_ord2 = opcode_list_ord
           # for block_id in loops_dict:
           #     parent = block_id
           #     opcode_list_ord.insert(opcode_list_ord.index(parent)+1, loop_list)
            for block_id in loops_dict2:
                parent = block_id
                #SLICE INDEXING IN LIST
                print(opcode_list_ord2)
                opcode_list_ord2[opcode_list_ord2.index(parent)+1:1] = loop_list2
                tmp_block3 = []
                for i in opcode_list_ord2:
                    tmp_block3.append(opcode_dict[i])
                print(tmp_block3)    
                #opcode_list_ord2.insert(opcode_list_ord2.index(parent)+1, loop_list2)
            #opcode_list_ord.insert(opcode_list_ord.index(before_blockid)+1, loop_list)
            scripts_dict[sprite].append(tmp_blocks)
            #print(opcode_list_ord)
            #print(opcode_dict)
            print(opcode_list_ord2)
            #print(tmp_blocks2)

        # Intra-sprite
        self.intra_dups_list = []
        for sprite in scripts_dict:
            blocks = scripts_dict[sprite]
            #print(blocks)
            dups = find_dups(blocks)
            if dups:
                self.intra_dups_list.append(dups[0])

        # Project-wide
        self.project_dups_list = []
        blocks = []
        for sprite in scripts_dict:
            blocks += scripts_dict[sprite]
        self.project_dups_list = find_dups(blocks)

    def finalize(self, filename):
        """Output the duplicate scripts detected."""
        with open(filename.replace('.json', '') + '-sprite.json',
                  'w') as outfile:
            json.dump(self.intra_dups_list, outfile)
        with open(filename.replace('.json', '') + '-project.json',
                  'w') as outfile:
            json.dump(self.project_dups_list, outfile)

        count = sum([len(listElem) for listElem in self.intra_dups_list])
        count = len(self.intra_dups_list)
        result = ("{} intra-sprite duplicate scripts found\n".format(count))
        result += ("%d project-wide duplicate scripts found\n" %
                   len(self.project_dups_list))
        return result


def get_function_blocks(start, block_dict):
    list_blocks = []
    begin = block_dict[block_dict[start]["next"]]
    while begin != None:
        list_blocks.append(begin["opcode"])
        if begin["next"] != None:
            begin = block_dict[begin["next"]]
        else:
            begin = None
    return list_blocks

def get_function_blocks_id(start, block_dict):
    """Get the block_ids inside loops"""
    list_blocks_id = []
    next_block_id = block_dict[start]["next"]
    next_block = block_dict[next_block_id]
    list_blocks_id.append(start)
    while next_block != None:
        list_blocks_id.append(next_block_id)
        if block_dict[next_block_id]["next"] != None:
            next_block_id = block_dict[next_block_id]["next"]
            next_block = block_dict[next_block_id]
        else:
            next_block = None
    return list_blocks_id

def getloop_ids(block_value, blocks_dict):
    loop_dict = {}
    list_loop = []
    parent = block_value["parent"]
    start = block_value["inputs"]["SUBSTACK"][1]
    list_function_blocks_id = get_function_blocks_id(start, blocks_dict)
    list_loop.append(blocks_dict[block_value["inputs"]["SUBSTACK"][1]]["parent"])
    list_loop.extend(list_function_blocks_id)
    loop_dict[block_value["parent"]] = list_loop
    #print(loop_dict)
    #print(list_loop)
    return list_loop

def getloopb(block_value, blocks_dict):
    loop_dict = {}
    list_loop = []
    parent = block_value["parent"]
    start = block_value["inputs"]["SUBSTACK"][1]
    list_function_blocks = get_function_blocks(start, blocks_dict)
    list_loop.append(block_value["opcode"])
    list_loop.append(blocks_dict[block_value["inputs"]["SUBSTACK"][1]]["opcode"])
    list_loop.extend(list_function_blocks)
    list_loop.append("CONTROL_END")
    loop_dict[block_value["parent"]] = list_loop
    #print(loop_dict)
    #print(list_loop)
    return list_loop

def loopb(filename):
    json_project = json.loads(open(filename).read())
    loop_list = []
    tmp_blocks = []

    for e in json_project["targets"]:
        sprite = e["name"]
        print(sprite)
        for k in e:
            if k == "blocks":
                list_custom = []
                for key in e[k]:
                    if e[k][key]["opcode"] in LOOP_BLOCKS:
                        parent = e[k][key]["inputs"]["SUBSTACK"][1]
                        list_function_blocks = get_function_blocks(parent, e[k])
                        list_custom.append(e[k][key]["opcode"])
                        list_custom.append(e[k][parent]["opcode"])
                        list_custom.extend(list_function_blocks)
                        list_custom.append("CONTROL_END")
                        if e[k][key]["opcode"] == "control_if_else":
                            parent = e[k][key]["inputs"]["SUBSTACK2"][1]
                            list_function_blocks = get_function_blocks(parent, e[k])
                            list_custom.append(e[k][parent]["opcode"])
                            list_custom.extend(list_function_blocks)
                        loop_list.append(list_custom)
                    #else:
                    #    if e[k][key]["topLevel"]:
                    #        if tmp_blocks:
                    #            scripts_dict[sprite].append(tmp_blocks)
                    #    tmp_blocks = [e[k][key]["opcode"]]
                    #    else:
                    #        tmp_blocks.append(block["opcode"])
                    
    #print(loop_list)

def customb(filename):
    json_project = json.loads(open(filename).read())
    list_customblocks_sprite = []
    list_calls = []
    data = {}
    count_definitions = 0
    count_calls = 0
    custom_list = []
    for e in json_project["targets"]:
        for k in e:
            if k == "blocks":
                name = e["name"] #SPRITE NAME
                data = {}
                data[name] = [] # ATENCION A ESTE MODO DE INDEXAR LISTAS EN DICCIONARIOS
                list_calls = []
                is_stage = e["isStage"] # SIMPLEMENTE PARA SABER SI ES STAGE
                list_custom = []
                for key in e[k]:
                    #print(e[k][key])
                    if e[k][key]["opcode"] == "procedures_prototype":
                        parent = e[k][key]["parent"]
                        list_function_blocks = get_function_blocks(parent, e[k])
                        #print(e[k][key])
                        list_custom.append(e[k][key]["opcode"])
                        list_custom.append(e[k][key]["mutation"]["proccode"])
                        data[name].append({"type": "procedures_prototype", "name": e[k][key]["mutation"]["proccode"],
                                "argument_names":e[k][key]["mutation"]["argumentnames"],
                                "argument_ids": e[k][key]["mutation"]["argumentids"],
                                "blocks": list_function_blocks,
                                "n_calls": 0})
                        count_definitions += 1
                        list_custom.extend(list_function_blocks)
                        custom_list.append(list_custom)
                    elif e[k][key]["opcode"] == "procedures_call":
                        list_calls.append({"type": "procedures_call", "name": e[k][key]["mutation"]["proccode"],
                                            "argument_ids":e[k][key]["mutation"]["argumentids"]})
                        count_calls += 1
                for call in list_calls:
                    for procedure in data[name]:
                        #print(procedure["name"], procedure["type"], " ||| ", call)
                        if procedure["name"] == call["name"] and procedure["type"] == "procedures_prototype":
                            #print("encuentra llamada")
                            procedure["n_calls"] = procedure["n_calls"] + 1
                data[name] += list_calls
                list_customblocks_sprite.append(data)
    data = {"name": filename.split(".")[0], "custom_blocks": list_customblocks_sprite, "n_custom_blocks": count_definitions,
            "n_custom_blocks_calls": count_calls}

    print(count_definitions, " custom blocks found")
    print(count_calls, " custom blocks calls found")
    print(custom_list)

    with open(filename.replace('.json', '') + '-customsprite.json',
              'w') as outfile:
        json.dump(custom_list, outfile)


def main(filename, ignoring):
    """The entrypoint for the 'duplicateScripts' extension"""
    duplicate = DuplicateScripts(ignoring)
    print("Looking for duplicate scripts in", filename)
    print()
    duplicate.analyze(filename)
    loopb(filename)
    #customb(filename)
    print("Minimum number of blocks:", N_BLOCKS)
    print(duplicate.finalize(filename))


if __name__ == "__main__":
    try:
        if len(sys.argv) == 2:
            main(sys.argv[1], False)
        elif len(sys.argv) == 3 and str(sys.argv[2]) == "-i":
            print("\nYou are now ignoring blocks\n")
            main(sys.argv[1], True)
        else:
            raise IndexError
    except IndexError:
        sys.exit("\nUsage: python3 duplicateScriptsApprox.py" +
                 " <file(.SB3 or .JSON or .ZIP)> [-i]\n" +
                 "\n-i (OPTIONAL): Ignore blocks from IgnoreBlocks.txt\n")
    except:
        sys.exit("\nSomething unexpected happened: ", sys.exc_info()[0])
