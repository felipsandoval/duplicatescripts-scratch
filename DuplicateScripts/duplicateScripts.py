#!/usr/bin/python3
# -*- coding: utf-8 -*-

from difflib import SequenceMatcher
import json
import zipfile
import sys
import shutil
# import os # ver este tema en windows ?

N_BLOCKS = 6
LOOP_BLOCKS = ["control_repeat", "control_forever", "control_if",
               "control_if_else", "control_repeat_until"]
CONDITIONALS = ["control_if", "control_if_else", "control_repeat_until"]
CONTROL_MARKS = ["END_LOOP", "END_CONDITION", "END_LOOP_CONDITIONAL"]


def find_dups(blocks):
    """
    Given a list of sequences of blocks opcodes
    returns those subsequences that are duplicated
    """
    return_list = []
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            word = SequenceMatcher(None, blocks[i],
                                   blocks[j])
            match = word.find_longest_match(0, len(blocks[i]),
                                            0, len(blocks[j]))
            if match.size >= N_BLOCKS:
                return_list.append(blocks[i][match.a:match.a + match.size])
    return return_list


def blocks2ignore():
    """
    Open .TXT and parser the blocks opcodes that are going to be ignored
    as duplicated scripts
    """
    with open('IgnoreBlocks.txt') as file:
        ignore_list = file.read().splitlines()
    file.close()
    return ignore_list

# Esto se puede borrar ahora que se usa en program.py
def sb3_json_extraction(file_in):
    """
    Will change the file extention to .zip from a given a .sb3,
    then will return the .json file inside the Scratch project.
    """
    file_out = file_in.split(".")[0] + ".zip"
    shutil.copyfile(file_in, file_out)
    zip_file = zipfile.ZipFile(file_out, "r")
    list_files_name = zip_file.namelist()
    # Iterates over the file names to find .json
    for filename in list_files_name:
        if filename.endswith('.json'):
            json_file = zip_file.extract(filename)
    json_project = json.loads(open(json_file).read())
    # os.remove(file_out)
    return json_project

# Esto se puede borrar ahora que se usa en program.py
def obtaining_json(filename):
    """Obtains JSON file from different extentions"""
    try:
        json_files_list = []
        if filename.endswith(".zip"):
            # Creates a list with all JSON filenames
            zip_file = zipfile.ZipFile(filename, "r")
            list_filenames = zip_file.namelist()
            for file in list_filenames:
                if file.endswith('.json'):
                   # zip_file.extract(file)
                    json_files_list.append(file)
                return json_files_list
        elif filename.endswith(".json"):
            json_file = json.loads(open(filename).read())
        elif filename.endswith(".sb3"):
            json_file = sb3_json_extraction(filename)
    except FileNotFoundError:
        sys.exit("\nPlease, use a file that exists in directory\n")
    except:
        sys.exit("\nPlease, use a valid extension file like .SB3," +
                 " JSON or .ZIP\n")
    return json_file


def get_function_blocks_id(start, block_dict):
    """Get the block_ids inside loops"""
    list_blocks_id = []
    list_blocks_id.append(start)
    next_block_id = block_dict[start]["next"]
    # CASE: there is only a single block inside a loop or to list a condition
    if next_block_id is None:
        next_block = None
    else:
        next_block = block_dict[next_block_id]
    while next_block is not None:
        list_blocks_id.append(next_block_id)
        if block_dict[next_block_id]["next"] is not None:
            next_block_id = block_dict[next_block_id]["next"]
            next_block = block_dict[next_block_id]
        else:
            next_block = None
    return list_blocks_id


def get_function_blocks_opcode(start, block_dict):
    """Get the opcode value"""
    list_blocks = []
    begin = block_dict[block_dict[start]["next"]]
    while begin is not None:
        list_blocks.append(begin["opcode"])
        if begin["next"] is not None:
            begin = block_dict[begin["next"]]
        else:
            begin = None
    return list_blocks


def get_custominfo(block, custom_dict, sprite, block_dict):
    """Extract information from custom blocks"""
    try:
        list_blocks = get_function_blocks_opcode(block["parent"], block_dict)
        custom_dict[sprite].append({"type": "procedures_prototype",
                "name": block["mutation"]["proccode"],
                "argument_names": block["mutation"]["argumentnames"],
                "argument_ids": block["mutation"]["argumentids"],
                "blocks": list_blocks,
                "n_calls": 0})
    except KeyError:
        # COMENTARLE A GREGORIO QUE HAY CASOS EN LOS QUE NO EXISTE EL PARENT
        pass


def change_blockid2opcode(scripts_dict, sprite, opcode_dict, ignoreblock_list, ignore):
    """Changes block id for opcode"""
    for block in scripts_dict[sprite]:
        for j in range(len(block)):
            if block[j] not in CONTROL_MARKS:
                block[j] = opcode_dict[block[j]]
            if ignore:
                if block[j] in ignoreblock_list and block[j] not in CONTROL_MARKS:
                    # print("entré en un block que se tiene que ignorar")
                    block[j] = "IGNORED BLOCK, should delete"


def getloop_ids(block_value, blocks_dict, block_id):
    """Extract blockids from loops and conditional blocks"""
    try:  # hay casos que no tiene SUBSTACK, Ni SUBSTACK2..
        list_loop = []
        list_loop.append(block_id)
        start = block_value["inputs"]["SUBSTACK"][1]
        list_loop.append(block_id)
        if start is None:  # In case a loop does not have anything inside.
            return list_loop
        list_blocks_id = get_function_blocks_id(start, blocks_dict)
        list_loop.extend(list_blocks_id)
        if block_value["opcode"] in CONDITIONALS:
            list_loop.append("END_LOOP")
            start = block_value["inputs"]["CONDITION"][1]
            list_cond_id = get_function_blocks_id(start, blocks_dict)
            list_loop.extend(list_cond_id)
            list_loop.append("END_CONDITION")
            if block_value["opcode"] == "control_if_else":
                start = block_value["inputs"]["SUBSTACK2"][1]
                if start is not None:
                    list_blocks2_id = get_function_blocks_id(start, blocks_dict)
                    list_loop.extend(list_blocks2_id)
                list_loop.append("END_LOOP_CONDITIONAL")
        else:
            list_loop.append("END_LOOP")
        return list_loop
    except KeyError:
        return list_loop

def checkif_loop(block, blocks_dict, block_id, loops_dict, existloop):
    if block["opcode"] in LOOP_BLOCKS:
        existloop = True
        loop_list = getloop_ids(block, blocks_dict, block_id)
        try:
            if block["parent"] is not None:
                loops_dict[block["parent"]] = loop_list
            else:
                loops_dict["loopistop"] = loop_list
        except KeyError:
            loops_dict["loopistop"] = loop_list
    return loops_dict

def checkif_conditional(block, custom_dict, sprite, blocks_dict, list_calls, count_definitions, list_customb, count_calls):
    if block["opcode"] == "procedures_prototype":
        get_custominfo(block, custom_dict, sprite, blocks_dict)
        count_definitions += 1
    elif block["opcode"] == "procedures_call":
        list_calls.append({"type": "procedures_call",
                            "name": block["mutation"]["proccode"],
                            "argument_ids": block["mutation"]["argumentids"]})
        self.count_calls += 1
        for call in list_calls:
                # print(call)
            for procedure in custom_dict[sprite]:
                # print(procedure)
                if procedure["name"] == call["name"] and procedure["type"] == "procedures_prototype":
                    procedure["n_calls"] = procedure["n_calls"] + 1
        # custom_dict[sprite] += list_calls # ESTO FALLA WTF
        list_customb.append(custom_dict)
    return count_definitions, count_calls


class DuplicateScripts():
    """
    Analyzer of duplicate scripts in sb3 projects
    New version for Scratch 3.0
    """

    def __init__(self, ignoring):
        self.ignoringisactive = ignoring
        self.toplevel_list = []
        self.count_definitions = 0
        self.count_calls = 0
        self.customb_info = {}

    def analyze(self, filename, json_project):
        """Start parsering it"""
        self.blocks_dict = {}  # block id -> block value
        scripts_dict = {}
        ignoreblock_list = blocks2ignore()
        custom_dict = {}
        list_calls = []
        list_customb = []

        # Loops through all sprites (and canva/Stage "sprite" too)
        for sprites_dict in json_project["targets"]:
            sprite = sprites_dict["name"]
            scripts_dict[sprite] = []
            custom_dict[sprite] = []
            # Gets all blocks out of sprite
            for blocks, blocks_value in sprites_dict["blocks"].items():
                if isinstance(blocks_value, dict):
                    self.blocks_dict[blocks] = blocks_value

            loops_dict = {}
            opcode_dict = {}   # block id -> block opcode
            loop_list = []
            toplevel_list = []
            existloop = False

            for block_id, block in self.blocks_dict.items():
                opcode_dict[block_id] = block["opcode"]
                if block["opcode"] in LOOP_BLOCKS:
                    existloop = True
                    loop_list = getloop_ids(block, self.blocks_dict, block_id)
                    try:
                        if block["parent"] is not None:
                            loops_dict[block["parent"]] = loop_list
                        else:
                            loops_dict["loopistop"] = loop_list
                    except KeyError:
                        loops_dict["loopistop"] = loop_list
                if block["opcode"] == "procedures_prototype":
                    get_custominfo(block, custom_dict, sprite, self.blocks_dict)
                    self.count_definitions += 1
                elif block["opcode"] == "procedures_call":
                    list_calls.append({"type": "procedures_call",
                                       "name": block["mutation"]["proccode"],
                                       "argument_ids": block["mutation"]["argumentids"]})
                    self.count_calls += 1
                    for call in list_calls:
                            # print(call)
                        for procedure in custom_dict[sprite]:
                            # print(procedure)
                            if procedure["name"] == call["name"] and procedure["type"] == "procedures_prototype":
                                procedure["n_calls"] = procedure["n_calls"] + 1
                    # custom_dict[sprite] += list_calls # ESTO FALLA WTF
                    list_customb.append(custom_dict)
                if block["topLevel"]:
                    sucesive_list = self.search_next([], block_id)
                    scripts_dict[sprite].append(sucesive_list)
                    toplevel_list.append(block_id)

            if existloop:
                existloop = False
                self.addloopblock(loops_dict, scripts_dict, sprite)

            change_blockid2opcode(scripts_dict, sprite, opcode_dict,
                                  ignoreblock_list, self.ignoringisactive)
            # print(custom_dict[sprite])
        # print(scripts_dict)

        self.get_dup_intra_sprite(scripts_dict)
        self.get_dup_project_wide(scripts_dict)
        # self.get_customb_info()
        # Custom Blocks information
        self.customb_info = {"name": filename.split(".")[0],
                             "custom_blocks": list_customb,
                             "n_custom_blocks": self.count_definitions,
                             "n_custom_blocks_calls": self.count_calls}

    def get_dup_intra_sprite(self, scripts_dict):
        """Finds intra-sprite duplication"""
        self.intra_dups_list = []
        for sprite in scripts_dict:
            blocks = scripts_dict[sprite]
            dups = find_dups(blocks)
            if dups:
                self.intra_dups_list.append(dups[0])

    def get_dup_project_wide(self, scripts_dict):
        """Finds project-wide duplication"""
        self.project_dups_list = []
        blocks = []
        for sprite in scripts_dict:
            blocks += scripts_dict[sprite]
        self.project_dups_list = find_dups(blocks)

    def search_next(self, block_list, block_id):
        """Finds next"""
        block = self.blocks_dict[block_id]
        block_list.append(block_id)
        if block["next"] is not None:
            block_id = block["next"]
            block_list = self.search_next(block_list, block_id)
        return block_list

    def addloopblock(self, loops_dict, scripts_dict, sprite):
        """Adds loop block in all blocks from project"""
        for parent in loops_dict:
            for list in scripts_dict[sprite]:
                if parent == "loopistop":
                    list[0:1] = loops_dict[parent]
                    # Index distinto para loops top level
                elif parent in list:  # SLICE INDEXING LIST
                    position = list.index(parent)
                    # VER ESTO PORQUE BORRAR AL FINAL NO DEBERÍA SER PROBLEMA
                    if position+1 != len(list):
                        # print(list)
                        del list[position+1]  # PARA BORRAR LOOP Q DUPLICA
                        list[position+1:1] = loops_dict[parent]
                        # print(list)
                    else:  # en caso que sea la ultima pos
                        # print(list)
                        # print(parent)
                        # print(loops_dict[parent])
                        # print("VER ESTE TEMA")
                        # print(position)
                        # del list[position] # PARA BORRAR LOOP QUE DUPLICA
                        # list[position:1] = loops_dict[parent]
                        list.extend(loops_dict[parent])

    def finalize(self, filename):
        """Output the duplicate scripts detected."""
        with open(filename.replace('.json', '') + '-sprite.json',
                  'w') as outfile:
            json.dump(self.intra_dups_list, outfile)
        with open(filename.replace('.json', '') + '-project.json',
                  'w') as outfile:
            json.dump(self.project_dups_list, outfile)
        with open(filename.replace('.json', '') + '-customblocksinfo.json',
                  'w') as outfile:
            json.dump(self.customb_info, outfile)
        count = sum([len(listElem) for listElem in self.intra_dups_list])
        count = len(self.intra_dups_list)
        result = ("\n{} intra-sprite duplicate scripts found\n".format(count))
        result += ("%d project-wide duplicate scripts found\n" %
                   len(self.project_dups_list))
        result += (str(self.count_definitions) + " custom blocks found\n")
        result += (str(self.count_calls) + " custom blocks calls found\n")
        return result


def iniciate_duplicates(filename, json_file, ignoring):
    """
    Defines DuplicateScripts class and gives feedback
    on how many duplicates scripts are.
    """
    duplicate = DuplicateScripts(ignoring)
    print("Looking for duplicate scripts in", filename)
    print()
    duplicate.analyze(filename, json_file)
    print("Minimum number of blocks:", N_BLOCKS)
    print(duplicate.finalize(filename))


def main(filename, json_file, ignoring):
    """Main function of my script"""
    iniciate_duplicates(filename, json_file, ignoring)

# Esto se puede borrar luego. 
def antiguo_main(filename, ignoring):
    """Main function of my script"""
    json_project = obtaining_json(filename)
    if filename.endswith('.zip'):
        print("HAGO VARIOS o uno")
        for i in json_project:
            json_file = json.loads(open(i).read())
            iniciate_duplicates(i, json_file, ignoring)
    else:
        iniciate_duplicates(filename, json_project, ignoring)

# Esto se puede borrar luego. 
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
    except FileNotFoundError:
        sys.exit("\nPlease, use a file that exists in directory\n")
    else:
        sys.exit("\nSomething unexpected happened: ", sys.exc_info()[0])
