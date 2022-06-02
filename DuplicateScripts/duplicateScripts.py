#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval

from difflib import SequenceMatcher
import json
from textwrap import wrap
# import os "Esto para limpiar" un poco las carpetas que se crean.
# Ver compatibilidad para Windows


N_BLOCKS = 6 # Minimo numero de bloques para que se considere como duplicado

LOOP_BLOCKS = ["control_repeat", "control_forever", "control_if",
               "control_if_else", "control_repeat_until"]
CONDITIONALS = ["control_if", "control_if_else", "control_repeat_until"]
CONTROL_MARKS = ["END_LOOP", "END_IF", "END_ELSE", "END_LOOP_CONDITIONAL"]


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


def get_next_blocks(start, block_dict):
    """Get the next block_ids"""
    # SPECIAL CASE: there is only a single block inside a loop 
    # or to list a condition
    next_block_id = block_dict[start]["next"]
    b_inside_loop = []
    b_inside_loop.append(start)
    if next_block_id is None:
        n_block = None
    else:
        n_block = block_dict[next_block_id]
    while n_block is not None:
        b_inside_loop.append(next_block_id)
        if block_dict[next_block_id]["next"] is not None:
            next_block_id = block_dict[next_block_id]["next"]
            n_block = block_dict[next_block_id]
        else:
            n_block = None
    return b_inside_loop


def get_custominfo(block):
    """Extract information from custom blocks"""
    try:
        #list_blocks = get_custom_blocks(block["parent"], block_dict)
        #print(list_blocks)
        custom_info = {"type": "procedures_prototype",
                "custom_name": block["mutation"]["proccode"],
                "argument_names": block["mutation"]["argumentnames"],
                "blocks": block["parent"], #list_blocks,
                "n_calls": 0}
        return custom_info
    except KeyError:
        # COMENTARLE A GREGORIO QUE HAY CASOS EN LOS QUE NO EXISTE EL PARENT
        pass


def change_blockid2opcode(sprite, opcode_dict, ignore_list, ignore):
    """Changes block id for opcode"""
    for block in sprite:
        for j in range(len(block)):
            if block[j] not in CONTROL_MARKS:
                block[j] = opcode_dict[block[j]]
            if ignore:
                if block[j] in ignore_list and block[j] not in CONTROL_MARKS:
                    # print("entré en un block que se tiene que ignorar")
                    block[j] = "IGNORED_BLOCK" # bloque ignorado, se debe eliminar o sencillamente ignorar ????


def getloop_ids(block_value, blocks_dict, block_id):
    """Extract blockids from loops and conditional blocks"""
    try: 
        loop_list = []
        loop_list.append(block_id)
        start = block_value["inputs"]["SUBSTACK"][1] # What happens if a loop does not have inputs nor substack value ? ALL OF THEM MUST HAVE THIS
        if start is None:
            return loop_list
        b_inside_loop = get_next_blocks(start, blocks_dict)
        loop_list.extend(b_inside_loop)
        if block_value["opcode"] in CONDITIONALS:
            loop_list.append("END_IF")
            if block_value["opcode"] == "control_if_else":
                start = block_value["inputs"]["SUBSTACK2"][1]
                b_2_inside_loop = []
                if start is not None:
                    b_2_inside_loop = get_next_blocks(start, blocks_dict)
                loop_list.extend(b_2_inside_loop)
                loop_list.append("END_ELSE")
            # No tengo porque regresar todo lo que precede al loop. Solamente lo de dentro!!! 
            #loop_list.append("END_LOOP_CONDITIONAL")
        loop_list.append("END_LOOP")
        return loop_list
    except KeyError:
        print("HAY UN ERROR REVISAR ESTOOOO")
        return loop_list

class DuplicateScripts():
    """
    Analyzer of duplicate scripts within a .json
    New version for Scratch 3.0
    """

    def __init__(self, ignoring):
        self.ignoringisactive = ignoring
        self.toplevel_list = []
        self.many_custom_blocks = 0
        self.many_custom_calls = 0
        self.all_customs_blocks = {}

    def analyze(self, filename, json_project):
        """Start parsering it"""
        self.total_blocks = {}  # block id -> block value
        scripts_dict = {}
        ignore_list = blocks2ignore()
        custom_dict = {}
        list_calls = []
        list_customb = []
        toplevel_list = []

        # Loops through all sprites (and canva/Stage "sprite" too)
        for sprites_dict in json_project["targets"]:
            self.blocks_dict = {}  # block id -> block value
            sprite = sprites_dict["name"]
            scripts_dict[sprite] = []
            custom_dict[sprite] = []
            # Gets all blocks out of sprite
            for blocks, blocks_value in sprites_dict["blocks"].items():
                if isinstance(blocks_value, dict):
                    self.blocks_dict[blocks] = blocks_value
                    self.total_blocks[blocks] = blocks_value
                    # Se hacen separados porque el orden es aleatorio y no quiero buscar un blockid y que no exista

            loops_dict = {}
            opcode_dict = {}   # block id -> block opcode. THIS IS FOR EACH SPRITE
            loop_list = []
            existloop = False # EXISTE UN LOOP EN UN SPRITE ESPECÍFICO
            # Loops through all blocks within each sprite
            for block_id, block in self.blocks_dict.items():
                opcode_dict[block_id] = block["opcode"]
                if block["opcode"] in LOOP_BLOCKS: # Caso de Loops
                    existloop = True
                    loop_list = getloop_ids(block, self.blocks_dict, block_id)
                    try:
                        if block["parent"] is not None:
                            loops_dict[block["parent"]] = loop_list
                        else:
                            # Este opcode del loop es parent
                            scripts_dict[sprite].append(loop_list)
                            toplevel_list.append(block_id)
                    except KeyError:
                        # En casos que no existiese el valor de parent. SERIA MUY RARO.
                        print("QUE RARO. NO TIENE EL VALUE DE PARENT ESTE ELEMENTO: ", block["opcode"])
                
                # Caso de custom blocks
                if block["opcode"] == "procedures_prototype":
                    #print("ENTRO EN EL CUSTOM")
                    custom_dict[sprite].append(get_custominfo(block))
                    self.many_custom_blocks += 1
                elif block["opcode"] == "procedures_call":
                    list_calls.append({"type": "procedures_call",
                                       "name": block["mutation"]["proccode"],
                                       "argument_ids": block["mutation"]["argumentids"]})
                    self.many_custom_calls += 1
                    for call in list_calls:
                            # print(call)
                        for procedure in custom_dict[sprite]:
                            if procedure["custom_name"] == call["name"] and procedure["type"] == "procedures_prototype":
                                procedure["n_calls"] = procedure["n_calls"] + 1
                    list_customb.append(custom_dict)
                
                # Caso de que sea topLevel.
                if block["topLevel"] and block["opcode"] not in LOOP_BLOCKS:
                    sucesive_list = self.search_next([], block_id)
                    scripts_dict[sprite].append(sucesive_list)
                    toplevel_list.append(block_id)
            
            # Para agregar campo de bloques en cada custom
            iterate = 0
            while len(custom_dict[sprite]) != iterate:
                j = 0
                for j in custom_dict[sprite]:
                    for k in scripts_dict[sprite]:
                        if j["blocks"] in k:
                            j["blocks"] = k
                iterate += 1

            if existloop:
                self.add_loop_block(loops_dict, scripts_dict, sprite)

            #print(scripts_dict[sprite])

            change_blockid2opcode(scripts_dict[sprite], opcode_dict,
                                  ignore_list, self.ignoringisactive)
 
        #print(scripts_dict)
        #print(custom_dict)
        self.get_dup_intra_sprite(scripts_dict)
        self.get_dup_project_wide(scripts_dict)
        self.all_customs_blocks = {"name": filename.split(".")[0],
                             "custom_blocks": list_customb,
                             "number_custom_blocks": self.many_custom_blocks,
                             "number_custom_blocks_calls": self.many_custom_calls}

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

    def add_loop_block(self, loops_dict, scripts_dict, sprite):
        """Adds loop block in all blocks from project"""
        for parent in loops_dict:
            for list in scripts_dict[sprite]:
                if parent in list:  # SLICE INDEXING LIST
                    position = list.index(parent)
                    if position+1 != len(list):
                        del list[position+1]  # PARA BORRAR LOOP Q DUPLICA
                        # list.pop(position+1)  # OTRA FORMA DE HACER LO DE ARRIBA
                        list[position+1:1] = loops_dict[parent]
                    else:
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
            json.dump(self.all_customs_blocks, outfile)
        count = sum([len(listElem) for listElem in self.intra_dups_list])
        count = len(self.intra_dups_list)
        result = ("\n{} intra-sprite duplicate scripts found\n".format(count))
        result += ("%d project-wide duplicate scripts found\n" %
                   len(self.project_dups_list))
        result += (str(self.many_custom_blocks) + " custom blocks found in all project\n")
        result += (str(self.many_custom_calls) + " custom blocks calls found in all project\n")
        return result


def main(filename, json_file, ignoring):
    """
    Defines DuplicateScripts class and gives feedback
    on how many duplicates scripts are.
    """
    duplicate = DuplicateScripts(ignoring)
    print("\n-- STARTING DUPLICATESCRIPTS.PY SCRIPT --\n")
    print("Looking for duplicate blocks in", filename)
    print()
    duplicate.analyze(filename, json_file)
    print("Minimum number of blocks: ", N_BLOCKS)
    print(duplicate.finalize(filename))
    # Una buena forma de depurar es comprobar la cantidad de elementos presentes en el array de blocks (numero total de bloques) y luego compararlo con la estructura obtenida. 
    # Deben coincidir en número 
    print("\n-- END OF DUPLICATESCRIPTS.PY SCRIPT --\n")