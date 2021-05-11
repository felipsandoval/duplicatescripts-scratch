#!/usr/bin/python3
# -*- coding: utf-8 -*-

from difflib import SequenceMatcher
import json
import zipfile
import sys
import shutil
import os

N_BLOCKS = 6
LOOP_BLOCKS = ["control_repeat", "control_forever", "control_if",
               "control_if_else", "control_repeat_until"]
CONDITIONALS = ["control_if", "control_if_else", "control_repeat_until"]

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
    except FileNotFoundError:
        sys.exit("\nPlease, use a file that exists in directory\n")
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
        script_dict_test = {}
        ignoreblock_list = blocks2ignore()
        loops_dict = {}
        custom_dict = {}

        # Loops through all sprites (and canva "sprite" too)
        for sprites_dict in json_project["targets"]:
            sprite = sprites_dict["name"]
            self.blocks_dict = {}
            scripts_dict[sprite] = []
            script_dict_test[sprite] = []
            # Gets all blocks out of sprite
            for blocks, blocks_value in sprites_dict["blocks"].items():
                if isinstance(blocks_value, dict):
                    self.blocks_dict[blocks] = blocks_value


            opcode_dict = {}   # block id -> block opcode
            tmp_blocks = []
            loop_list = []
            tmp_blocks_loop = []
            topLevel_list = []
            existloop = False

            for block_id, block in self.blocks_dict.items():
                opcode_dict[block_id] = block["opcode"]
                if block["opcode"] in LOOP_BLOCKS:
                    existloop = True
                    loop_list = getloop_ids(block, self.blocks_dict, block_id)
                    if block["parent"] != None:
                        loops_dict[block["parent"]] = loop_list
                    else:
                        loops_dict["loopistop"] = loop_list
                    #print(loops_dict)
                    # ESTO FUNCIONA
                if block["opcode"] == "procedures_prototype":
                    print("tengo un bloque personalizado hacer proceso de apéndice de info")
                    getcustominfo(block)
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
                        testing = self.search_next([], block_id)
                        script_dict_test[sprite].append(testing)
                        if tmp_blocks: 
                            scripts_dict[sprite].append(tmp_blocks)
                        tmp_blocks = [block["opcode"]]
                        topLevel_list.append(block_id)
                    else:
                        tmp_blocks.append(block["opcode"])
            scripts_dict[sprite].append(tmp_blocks)

            if existloop:
                existloop = False
                for block_id in loops_dict:
                    parent = block_id
                    for i in script_dict_test[sprite]:
                        try:
                            if parent in i: #SLICE INDEXING IN LIST
                                del i[i.index(parent)+1] # PARA BORRAR EL LOOP QUE SE DUPLICA
                                i[i.index(parent)+1:1] = loops_dict[parent]
                            elif parent == "loopistop":
                                i[0:1] = loops_dict[parent] # Index distinto para los loops que son top level
                        except:
                            print("un objeto vacío")
                            pass
    
            #CAMBIANDO VALOR DE BLOCK_ID POR OPCODE. FUNCIONA CON CONTROL_REPEAT
            for block in script_dict_test[sprite]:
                for j in range(len(block)):
                    #print(block[j])
                    if block[j] != "END_LOOP" and block[j] != "END_CONDITION" and block[j] != "END_LOOP_CONDITIONAL":
                        opcode = opcode_dict[block[j]]
                        block[j] = opcode
        print(script_dict_test)

        scripts_dict = script_dict_test
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

    def search_next(self, block_list, block_id):

        block = self.blocks_dict[block_id]
        block_list.append(block_id)
        next_block = block["next"]
        if block["next"] == None:
            return block_list
        else:
            block_id = next_block
            block_list = self.search_next(block_list, block_id)
        return block_list

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

def get_function_blocks_id(start, block_dict):
    """Get the block_ids inside loops"""
    list_blocks_id = []
    list_blocks_id.append(start)
    next_block_id = block_dict[start]["next"]
    #N0 LE PUEDO PASAR UN START QUE ESTE NULO O SEA
    if next_block_id == None:
        next_block = None
    else:
        next_block = block_dict[next_block_id]
    while next_block != None:
        list_blocks_id.append(next_block_id)
        if block_dict[next_block_id]["next"] != None:
            next_block_id = block_dict[next_block_id]["next"]
            next_block = block_dict[next_block_id]
        else:
            next_block = None
    return list_blocks_id

def getcustominfo(blocks):
    print("terminar esto")

def getloop_ids(block_value, blocks_dict, block_id):
    list_loop = []
    try:
        start = block_value["inputs"]["SUBSTACK"][1]
        if start == None:
            list_loop.append(block_id)
            return list_loop
        list_function_blocks_id = get_function_blocks_id(start, blocks_dict)
    except:
        list_loop.append(block_id)
        return list_loop
    #list_loop.append(blocks_dict[block_value["inputs"]["SUBSTACK"][1]]["parent"])
    list_loop.append(block_id) # es lo mismo que arriba, menos enrevesado
    list_loop.extend(list_function_blocks_id)
    if block_value["opcode"] in CONDITIONALS:
        list_loop.append("END_LOOP")
        start = block_value["inputs"]["CONDITION"][1]
        testing_cond = get_function_blocks_id(start, blocks_dict)
        if block_value["opcode"] == "control_if_else":
            list_loop.extend(testing_cond)
            list_loop.append("END_CONDITION")
            start = block_value["inputs"]["SUBSTACK2"][1]
            list_loop_conditional = get_function_blocks_id(start, blocks_dict)
            list_loop.extend(list_loop_conditional)
            list_loop.append("END_LOOP_CONDITIONAL")
        else:
            list_loop.extend(testing_cond)
            list_loop.append("END_CONDITION")
    else:
        list_loop.append("END_LOOP")
    return list_loop


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
                        #list_custom.append(e[k][key]["mutation"]["proccode"])
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
    except FileNotFoundError:
        sys.exit("\nPlease, use a file that exists in directory\n")
    except:
        sys.exit("\nSomething unexpected happened: ", sys.exc_info()[0])
