#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Made by Felipe E. Sandoval Sibada

import duplicateScripts
import statistics
import cluster
import most_frequent_blocks
import sys
from os import walk
from datetime import datetime
import shutil
import json
import zipfile
import os

#startTime = datetime.now()

#print(datetime.now() - startTime)

#mypath = sys.argv[1]
#_, _, filenames = next(walk(mypath))
#for filename in filenames:
#    duplicateScripts.main(mypath + filename)
    #statistics.main(filename + "-intra.json")
    #statistics.main(filename + "-project.json")
#    cluster.main(mypath + filename.replace(".json", "") + "-project.json")


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
            json_file = json_file.split("/")[-1]
    json_project = json_file
    os.remove(fileOut)
    return json_project

def obtaining_json(filename):
    """Obtains JSON"""
    try:
        if filename.endswith(".zip"):
            zip_file = zipfile.ZipFile(filename, "r")
            # Aquí hay que hacer el caso en el que sean VARIOS archivos JSON.
            json_file = "project.json"
        elif filename.endswith(".json"):
            json_file = filename
            return json_file
        elif filename.endswith(".sb3"):
            json_file = sb3_json_extraction(filename)
    except FileNotFoundError:
        sys.exit("\nPlease, use a file that exists in directory\n")
    except:
        sys.exit("\nPlease, use a valid extension file like .SB3," +
        " JSON or .ZIP\n")
    return json_file

def main(filename, ignoring):
    """MAIN PROGRAM"""
    print("\n-- STARTING ANALYSIS --\n")
    json_file = obtaining_json(filename)
    print(json_file)
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
    # except TypeError:
    #   sys.exit("\nPlease, use a valid extension file like .SB3," +
    #   " JSON or .ZIP\n")
    except:
        sys.exit("\nSomething unexpected happened: ", sys.exc_info()[0])