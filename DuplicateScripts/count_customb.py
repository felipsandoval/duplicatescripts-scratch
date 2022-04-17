import json
import pymongo
from os import listdir
from os.path import isfile, join
import sys
import os
import zipfile

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

mypath = "./projects_sb3/"
new_path = "./sb3/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
print("TEST FILES", onlyfiles[0])

db = pymongo.MongoClient(host="f-l2108-pc01.aulas.etsit.urjc.es", port=21000)
#db = pymongo.MongoClient(host="localhost", port=27017)
db = db["ct_blocks"]
col_custom = db["customblocks"]

#filename = "490319019.json"
for filename in onlyfiles:
    try:
        #zip_file = zipfile.ZipFile(filename, "r")
        #json_project = json.loads(zip_file.open("project.json").read())
        #print(json.dumps(json_project, indent=4, sort_keys=True))
        json_project = json.loads(open(mypath + filename, encoding="utf-8").read())
        list_customblocks_sprite = []
        list_calls = []
        data = {}
        count_definitions = 0
        count_calls = 0
        for e in json_project["targets"]:
            for k in e:
                if k == "blocks":
                    name = e["name"] #SPRITE NAME
                    data = {}
                    data[name] = [] # ATENCION A ESTE MODO DE INDEXAR LISTAS EN DICCIONARIOS
                    list_calls = []
                    is_stage = e["isStage"] # SIMPLEMENTE PARA SABER SI ES STAGE
                    for key in e[k]:
                        print(e[k][key])
                        try:
                            if e[k][key]["opcode"] == "procedures_prototype":
                                parent = e[k][key]["parent"]
                                list_function_blocks = get_function_blocks(parent, e[k])
                                print(e[k][key])
                                data[name].append({"type": "procedures_prototype", "name": e[k][key]["mutation"]["proccode"],
                                        "argument_names":e[k][key]["mutation"]["argumentnames"],
                                        "argument_ids": e[k][key]["mutation"]["argumentids"],
                                        "blocks": list_function_blocks,
                                        "n_calls": 0})
                                count_definitions += 1
                            elif e[k][key]["opcode"] == "procedures_call":
                                list_calls.append({"type": "procedures_call", "name": e[k][key]["mutation"]["proccode"],
                                                   "argument_ids":e[k][key]["mutation"]["argumentids"]})
                                count_calls += 1

                        except Exception as e:
                            pass
                    for call in list_calls:
                        for procedure in data[name]:
                            print("Comprueba")
                            print(procedure["name"], procedure["type"], " ||| ", call)
                            if procedure["name"] == call["name"] and procedure["type"] == "procedures_prototype":
                                print("encuentra llamada")
                                procedure["n_calls"] = procedure["n_calls"] + 1
                    data[name] += list_calls
                    list_customblocks_sprite.append(data)
        data = {"name": filename.split(".")[0], "custom_blocks": list_customblocks_sprite, "n_custom_blocks": count_definitions,
                "n_custom_blocks_calls": count_calls}
        col_custom.insert_one(data)

        print(filename, ": Number of custom blocks", count_definitions, count_calls)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(filename, "could not be analyzed")