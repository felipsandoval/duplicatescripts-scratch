#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Made by Felipe E. Sandoval Sibada

import duplicateScripts
import statistics
import cluster
import most_frequent_blocks
import sys
from datetime import datetime
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
    # os.remove(fileOut)
    return json_project

def define_duplicates(filename, json_file, ignoring):
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

def main(filename, ignoring):
    """MAIN PROGRAM"""
    print("\n-- STARTING ANALYSIS --\n")
    duplicateScripts.main(filename, ignoring)
    most_frequent_blocks.main(filename)
    spritefile = filename.replace('.json', '') + '-sprite.json'
    projectfile = filename.replace('.json', '') + '-project.json'
    print("\n-- INTRA SPRITE STATISTICS --\n")
    statistics.main(spritefile)
    print("\n-- INTRA PROJECT STATISTICS --\n")
    statistics.main(projectfile)
    print("\n-- CLUSTER SCRIPT --\n")
    cluster.main(filename)

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
    #except:
    #    sys.exit("\nSomething unexpected happened: ", sys.exc_info()[0])