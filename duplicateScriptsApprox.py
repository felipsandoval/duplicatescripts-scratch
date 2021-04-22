#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Made by Felipe E. Sandoval Sibada

from difflib import SequenceMatcher
import json
import zipfile
import sys
import os
import pathlib
import shutil

N_BLOCKS = 6
Ignore = 3
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
    Open .TXT and parser the blocks that are going to be ignored
    as duplicated
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


class DuplicateScripts():
    """
    Analyzer of duplicate scripts in sb3 projects
    New version for Scratch 3.0
    """

    def __init__(self, ignoring):
        #  self.blocks_dict = {}
        #  self.all_blocks = []
        self.ignoringisactive = ignoring
        self.list_duplicate = []
        self.blocks_dup = {}
        self.toplevel_list = []
        self.nextnull_list = []
        self.parentnull_list = {}
        #  self.list_duplicate_string = []

    def analyze(self, filename):
        """Obtains JSON and start parsering it"""
        if filename.endswith(".zip"):
            zip_file = zipfile.ZipFile(filename, "r")
            # Aquí hay que hacer el caso en el que sean VARIOS archivos JSON.
            json_project = json.loads(zip_file.open("project.json").read())
        elif filename.endswith(".json"):
            json_project = json.loads(open(filename).read())
        elif filename.endswith(".sb3"):
            json_project = sb3_json_extraction(filename)
        else:
            raise TypeError

        scripts_dict = {}
        ignoreblock_list = blocks2ignore()

        # Loops through all sprites (all sprites + 1 for canva sprite)
        for sprites_dict in json_project["targets"]:
            sprite = sprites_dict["name"]
            blocks_dict = {}
            scripts_dict[sprite] = []
            self.parentnull_list[sprite] = []
            # Gets all blocks out of sprite
            for blocks, blocks_value in sprites_dict["blocks"].items():
                if isinstance(blocks_value, dict):
                    blocks_dict[blocks] = blocks_value
            opcode_dict = {}   # block id -> opcode
            #toplevel_list = []  # list of top-level block ids
            tmp_blocks = []
            for block_id, block in blocks_dict.items():
                opcode_dict[block_id] = block["opcode"]
                if self.ignoringisactive:
                    if block["opcode"] not in ignoreblock_list:
                        if block["topLevel"]:
                            #print(tmp_blocks)
                            if tmp_blocks:
                                scripts_dict[sprite].append(tmp_blocks)
                            self.toplevel_list.append(block_id)
                            self.parentnull_list[sprite].append(block_id)
                            tmp_blocks = [block["opcode"]]
                        else:
                            tmp_blocks.append(block["opcode"])
                        #if block["next"] == None:
                        #    self.nextnull_list.append(block_id)
                        #if block["parent"] == None: #PARENT NO SIEMPRE ESTÁ EN TODOS LOS SPRITES??
                        #    self.parentnull_list.append(block_id)
                        #print(tmp_blocks)
                    else:
                        print("IGNORO BLOQUE")
                else:
                    if block["topLevel"]:
                        #print(tmp_blocks)
                        if tmp_blocks:
                            scripts_dict[sprite].append(tmp_blocks)
                        self.toplevel_list.append(block_id)
                        self.parentnull_list[sprite].append(block_id)
                        tmp_blocks = [block["opcode"]]
                    else:
                        tmp_blocks.append(block["opcode"])
            scripts_dict[sprite].append(tmp_blocks)

        print(scripts_dict)

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


def main(filename, ignoring):
    """The entrypoint for the 'duplicateScripts' extension"""
    duplicate = DuplicateScripts(ignoring)
    print("Looking for duplicate scripts in", filename)
    print()
    duplicate.analyze(filename)
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
    # except TypeError:
    #   sys.exit("\nPlease, use a valid extension file like .SB3," +
    #   " JSON or .ZIP\n")
    except:
        sys.exit("\nSomething unexpected happened: ", sys.exc_info()[0])
