#!/usr/bin/python3
# -*- coding: utf-8 -*-
# forked from davidrol6/duplicatescripts-scratch @davidrol6
# Github: @felipsandoval

from difflib import SequenceMatcher
import json

N_BLOCKS = 6  # Minimum number of blocks to be consider as duplicated

LOOP_BLOCKS = ["control_repeat", "control_forever", "control_if",
               "control_if_else", "control_repeat_until"]

CONDITIONALS = ["control_if", "control_if_else", "control_repeat_until"]

CONTROL_MARKS = ["END_LOOP", "END_IF", "END_ELSE"]


def find_dups(blocks):
    """
    Given a list of sequences of blocks opcodes
    returns those subsequences that are duplicated
    """
    temp_blocks = blocks
    return_list = []
    for i in range(len(temp_blocks)):
        for j in range(i + 1, len(temp_blocks)):
            word = SequenceMatcher(None, temp_blocks[i],
                                   temp_blocks[j])
            match = word.find_longest_match(0, len(temp_blocks[i]),
                                            0, len(temp_blocks[j]))
            if match.size >= N_BLOCKS:
                return_list.append(temp_blocks[i][match.a:match.a + match.size])
                temp_blocks[j] = ["listo", "revisado"]
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


def get_next_blocks(start, blocks_dict):
    """Get the next block_ids"""
    # SPECIAL CASE: there is only a single block inside a loop
    b_inside_loop = []
    b_inside_loop.append(start)
    if start in blocks_dict:
        next_block_id = blocks_dict[start]["next"]
    else:
        next_block_id = None
    if next_block_id is None:
        n_block = None
    else:
        n_block = blocks_dict[next_block_id]
    while n_block is not None:
        b_inside_loop.append(next_block_id)
        if blocks_dict[next_block_id]["next"] is not None:
            next_block_id = blocks_dict[next_block_id]["next"]
            n_block = blocks_dict[next_block_id]
        else:
            n_block = None
    return b_inside_loop


def change_blockid(scripts_list, opcode_dict, ignore):
    """Changes block id for opcode and returns how many opcodes ignores"""
    ignored = 0
    ignore_list = blocks2ignore()
    for script in scripts_list:
        i = 0
        while i < len(script):
            if script[i] not in CONTROL_MARKS:
                script[i] = opcode_dict[script[i]]
            if ignore and script[i] in ignore_list:
                script.pop(i)
                ignored += 1
            else:
                i += 1
    return ignored


def getloop_ids(block_value, blocks_dict, block_id):
    """Extract blockids from loops and conditional blocks"""
    loop_list = []
    # loop_list.append(block_id)
    if "SUBSTACK" in block_value["inputs"]:
        start = block_value["inputs"]["SUBSTACK"][1]
        if start is not None:
            b_inside_loop = get_next_blocks(start, blocks_dict)
            loop_list.extend(b_inside_loop)
    # What happens if a loop does not have this value ?
    if block_value["opcode"] in CONDITIONALS:
        loop_list.append("END_IF")
        if block_value["opcode"] == "control_if_else":
            b_2_inside_loop = []
            if "SUBSTACK2" in block_value["inputs"]:
                start = block_value["inputs"]["SUBSTACK2"][1]
                if start is not None:
                    b_2_inside_loop = get_next_blocks(start, blocks_dict)
                    loop_list.extend(b_2_inside_loop)
            # What happens if a loop does not have this value ?
            loop_list.append("END_ELSE")
    loop_list.append("END_LOOP")
    return loop_list


def add_loop_block(loops_dict, scripts_dict, sprite):
    """Adds loop block in all blocks from project"""
    for parent in loops_dict:
        for list in scripts_dict[sprite]:
            if parent in list:  # SLICE INDEXING LIST
                pos = list.index(parent)
                if pos+1 != len(list):
                    if list[pos+1] == loops_dict[parent][0]:
                        del list[pos+1]  # DELETE DUPLICATE LOOP
                    list[pos+1:1] = loops_dict[parent]
                else:
                    list.extend(loops_dict[parent])
    return scripts_dict


def get_custominfo(block):
    """Extract information from custom blocks"""
    custom_info = {"type": "procedures_prototype",
                   "custom_name": block["mutation"]["proccode"],
                   "argument_names": block["mutation"]["argumentnames"],
                   "n_calls": 0}
    if "parent" in block:
        custom_info.update({"blocks": block["parent"]})
    else:
        custom_info.update({"blocks": "empty"})
    return custom_info


def get_totalblocks(scripts_dict):
    """Return total blocks from my project"""
    total = 0
    ignore_list = blocks2ignore()
    for sprite in scripts_dict:
        for script in scripts_dict[sprite]:
            for block in script:
                if block not in ignore_list:
                    total += 1
    return total


def add_custom_call(block, custom_dict, sprite):
    for j in custom_dict[sprite]:
        if j["custom_name"] == block["mutation"]["proccode"]:
            j["n_calls"] = j["n_calls"] + 1
    return custom_dict


def add_blocks(scripts_dict, custom_dict, sprite):
    iterate = 0
    while len(custom_dict[sprite]) != iterate:
        for j in custom_dict[sprite]:
            for k in scripts_dict[sprite]:
                if j["blocks"] in k:
                    j["blocks"] = k
        iterate += 1
    return custom_dict


class DuplicateScripts():
    """
    Analyzer of duplicate scripts within a .json
    New version for Scratch 3.0
    """

    def __init__(self, ignoring):
        self.ignore = ignoring
        self.total_blocks = 0
        self.total_ignored = 0
        self.total_scripts = 0
        self.total_sprites = 0
        self.total_custom_blocks = 0
        self.total_custom_calls = 0
        self.all_customs_blocks = {}
        self.toplevel_list = []

    def analyze(self, filename, json_project):
        """Start parsering it"""
        scripts_dict = {}
        custom_dict = {}
        list_customb = []
        # Loops through all sprites
        for sprites_dict in json_project["targets"]:
            self.blocks_dict = {}  # block id -> block value
            sprite = sprites_dict["name"]
            scripts_dict[sprite] = []
            custom_dict[sprite] = []
            # Gets all blocks out of sprite
            for blocks, blocks_value in sprites_dict["blocks"].items():
                if isinstance(blocks_value, dict):
                    self.blocks_dict[blocks] = blocks_value
                    # self.total_blocks += 1
            loops_dict = {}
            opcode_dict = {}   # block id -> block opcode.
            loop_list = []
            # Loops through all blocks within each sprite
            for block_id, block in self.blocks_dict.items():
                opcode_dict[block_id] = block["opcode"]
                if block["opcode"] in LOOP_BLOCKS:
                    loop_list = getloop_ids(block, self.blocks_dict, block_id)
                    if "parent" in block and block["parent"] is not None:
                        if block["parent"] in self.blocks_dict and\
                           self.blocks_dict[block["parent"]]["opcode"] not in LOOP_BLOCKS:
                            loop_list.insert(0, block_id)
                            loops_dict[block["parent"]] = loop_list
                        else:
                            loops_dict[block_id] = loop_list
                    else:
                        scripts_dict[sprite].append(loop_list)
                        self.toplevel_list.append(block_id)
                elif block["opcode"] == "procedures_prototype":
                    custom_dict[sprite].append(get_custominfo(block))
                    self.total_custom_blocks += 1
                elif block["opcode"] == "procedures_call":
                    self.total_custom_calls += 1
                    list_customb.append(add_custom_call(block,
                                                        custom_dict, sprite))
                if block["topLevel"] and block["opcode"] not in LOOP_BLOCKS:
                    sucesive_list = self.search_next([], block_id)
                    scripts_dict[sprite].append(sucesive_list)
                    self.toplevel_list.append(block_id)

            # Add blocks to custom
            if bool(custom_dict[sprite]):
                custom_dict = add_blocks(scripts_dict, custom_dict, sprite)
            # Add blocks to loops
            if bool(loops_dict):
                scripts_dict = add_loop_block(loops_dict, scripts_dict, sprite)
            self.total_ignored += change_blockid(scripts_dict[sprite],
                                                 opcode_dict, self.ignore)
            self.total_sprites += 1
            self.total_scripts += len(scripts_dict[sprite])
        self.total_blocks = get_totalblocks(scripts_dict)
        self.get_dup_intra_sprite(scripts_dict)
        #print(scripts_dict)
        self.get_dup_project_wide(scripts_dict)
        self.all_customs_blocks = {"name": filename,
                                   "custom_blocks": list_customb,
                                   "number_custom_blocks":
                                   self.total_custom_blocks,
                                   "number_custom_blocks_calls":
                                   self.total_custom_calls}

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

    def finalize(self, filename):
        """Output the duplicate scripts detected."""
        with open(filename + '-sprite.json',
                  'w') as outfile:
            json.dump(self.intra_dups_list, outfile)
        with open(filename + '-project.json',
                  'w') as outfile:
            json.dump(self.project_dups_list, outfile)
        with open(filename + '-custom.json',
                  'w') as outfile:
            json.dump(self.all_customs_blocks, outfile)
        count = sum([len(listElem) for listElem in self.intra_dups_list])
        count = len(self.intra_dups_list)
        result = ("\n" + str(self.total_blocks) +
                  " total blocks found\n")
        result += (str(self.total_scripts) + " total scripts found\n")
        result += (str(self.total_sprites) + " total sprites found\n")
        result += (str(self.total_ignored) + " total blocks ignored\n")
        result += ("{} intra-sprite duplicate scripts found\n".format(count))
        result += ("%d project-wide duplicate scripts found\n" %
                   len(self.project_dups_list))
        result += (str(self.total_custom_blocks) +
                   " custom blocks found in all project\n")
        result += (str(self.total_custom_calls) +
                   " custom blocks calls found in all project\n")
        return result


def main(filename, json_file, ignoring):
    """
    Defines DuplicateScripts class and gives feedback
    on how many duplicates scripts are.
    """
    duplicate = DuplicateScripts(ignoring)
    print("\n-- STARTING DUPLICATESCRIPTS.PY SCRIPT --\n")
    print("Looking for duplicate blocks in", filename, "\n")
    duplicate.analyze(filename, json_file)
    print("Minimum number of blocks: ", N_BLOCKS)
    print(duplicate.finalize(filename.split(".")[0]))
    print("\n-- END OF DUPLICATESCRIPTS.PY SCRIPT --\n")
