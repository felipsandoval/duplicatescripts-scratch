#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval

# My Scripts / Libraries 
import duplicateScripts
import statistics
import cluster
import most_frequent_blocks

import sys
import shutil
import json
import zipfile


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
    # os.remove(fileOut) ver este tema en windows
    return json_project


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


def analyze(filename, ignoring, json, type_of_file):
    """Analizing process"""
    duplicateScripts.main(filename, json, ignoring)
    most_frequent_blocks.main(json)
    spritefile = filename.replace(type_of_file, '') + '-sprite.json'
    projectfile = filename.replace(type_of_file, '') + '-project.json'
    print("\n-- GETTING INTRA SPRITE STATISTICS --\n")
    statistics.main(spritefile)
    print("\n-- GETTING INTRA PROJECT STATISTICS --\n")
    statistics.main(projectfile)
    print("\n-- STARTING CLUSTER.PY SCRIPT --\n")
    cluster.main(filename)
    print("\n-- END OF CLUSTER.PY SCRIPT --\n")


def main(filename, ignoring):
    """MAIN PROGRAM"""
    print("\n*** STARTING ANALYSIS ***\n")
    json_project = obtaining_json(filename)
    if filename.endswith('.zip'):
        # Ahondar un poco más en casos donde se tengan que hacer un montón de ficheros
        for i in json_project:
            json_file = json.loads(open(i).read())
            analyze(filename, ignoring, json_file, '.zip')
    else:
        analyze(filename, ignoring, json_project, '.json')

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
        sys.exit("\nPlease, use a file that exists in your current directory\n")
    #except:
    #    sys.exit("\nSomething unexpected happened: ", sys.exc_info()[0])