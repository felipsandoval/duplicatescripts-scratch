#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval

from difflib import SequenceMatcher
import json
import opcode
# import os "Esto para limpiar" un poco las carpetas que se crean.
# Ver compatibilidad para Windows


N_BLOCKS = 6 # Minimo numero de bloques para que se considere como duplicado

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


def get_blocks_in_loop(start, block_dict):
    """Get the block_ids inside a loop"""
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


# Esta función y la de arriba son la misma. Estudiarla más a fondo y unificarlas.
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


def change_blockid2opcode(scripts_dict, sprite, opcode_dict, ignore_list, ignore):
    """Changes block id for opcode"""
    for block in scripts_dict[sprite]:
        for j in range(len(block)):
            if block[j] not in CONTROL_MARKS:
                block[j] = opcode_dict[block[j]]
            if ignore:
                if block[j] in ignore_list and block[j] not in CONTROL_MARKS:
                    # print("entré en un block que se tiene que ignorar")
                    block[j] = "IGNORED_BLOCK" #bloque ignorado, se debe eliminar o sencillamente ignorar ????


def getloop_ids(block_value, blocks_dict, block_id):
    """Extract blockids from loops and conditional blocks"""
    try: 
        loop_list = []
        loop_list.append(block_id)
        start = block_value["inputs"]["SUBSTACK"][1] # What happens if a loop does not have inputs nor substack value ? ALL OF THEM MUST HAVE THIS
        if start is None:
            return loop_list
        b_inside_loop = get_blocks_in_loop(start, blocks_dict)
        loop_list.extend(b_inside_loop)

        if block_value["opcode"] in CONDITIONALS:
            loop_list.append("END_CONDITION")
            if block_value["opcode"] == "control_if_else":
                start = block_value["inputs"]["SUBSTACK2"][1]
                b_2_inside_loop = []
                if start is not None:
                    b_2_inside_loop = get_blocks_in_loop(start, blocks_dict)
                loop_list.extend(b_2_inside_loop)
                loop_list.append("END_CONDITION")
            # No tengo porque regresar todo lo que precede al loop. Solamente lo de dentro!!! 
            #start = block_value["next"]
            #b_next_loop = []
            #if start is not None:
            #    b_next_loop = get_blocks_in_loop(start, blocks_dict)
            #    loop_list.extend(b_next_loop)
            #loop_list.append("END_LOOP_CONDITIONAL")
            #return loop_list
            #LAS CONDICIONES. NO SE SI HAY QUE TENERLAS EN CUENTA. yo diría que NO.
        loop_list.append("END_LOOP")
        return loop_list
    except KeyError:
        print("HAY UN ERROR REVISAR ESTOOOO")
        return loop_list

# No se usa. Ver si se puede borrar.
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
    Analyzer of duplicate scripts within a .json
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
                            #loops_dict["loopistop"] = loop_list
                            scripts_dict[sprite].append(loop_list)
                            toplevel_list.append(block_id)
                    except KeyError:
                        # En casos que no existiese el valor de parent. SERIA MUY RARO.
                        print("QUE RARO. NO TIENE EL VALUE DE PARENT ESTE ELEMENTO: ", block["opcode"])
                
                # Caso de custom blocks
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
                
                # Caso de que sea topLevel. REVISAR ESTO
                if block["topLevel"] and block["opcode"] not in LOOP_BLOCKS:
                    sucesive_list = self.search_next([], block_id)
                    scripts_dict[sprite].append(sucesive_list)
                    toplevel_list.append(block_id)


            if existloop:
                self.add_loop_block(loops_dict, scripts_dict, sprite)

            change_blockid2opcode(scripts_dict, sprite, opcode_dict,
                                  ignore_list, self.ignoringisactive)
            #print("Ahora imprimo TODOS los scripts de cada objeto. ", sprite)
            #print(scripts_dict[sprite])
            #print()
 
        #print(scripts_dict)

        self.get_dup_intra_sprite(scripts_dict)
        self.get_dup_project_wide(scripts_dict)
        # self.get_customb_info()
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

    def add_loop_block(self, loops_dict, scripts_dict, sprite):
        """Adds loop block in all blocks from project"""
        for parent in loops_dict:
            for list in scripts_dict[sprite]:
                if parent in list:  # SLICE INDEXING LIST
                    position = list.index(parent)
                    if position+1 != len(list):
                        del list[position+1]  # PARA BORRAR LOOP Q DUPLICA
                        #list.pop(position+1)  # OTRA FORMA DE HACER LO DE ARRIBA
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
            json.dump(self.customb_info, outfile)
        count = sum([len(listElem) for listElem in self.intra_dups_list])
        count = len(self.intra_dups_list)
        result = ("\n{} intra-sprite duplicate scripts found\n".format(count))
        result += ("%d project-wide duplicate scripts found\n" %
                   len(self.project_dups_list))
        result += (str(self.count_definitions) + " custom blocks found\n")
        result += (str(self.count_calls) + " custom blocks calls found\n")
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