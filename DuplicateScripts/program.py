#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval

# My Scripts
import duplicateScripts
import statistics
import cluster
import most_frequent_blocks

# Modules used
import traceback
import sys
import os
import shutil
import json
import zipfile
import logging  # Module used to store detailed events in a log file


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
    zip_file.close()
    os.remove(fileOut)  # Deletes the created ZIP file
    return json_project


def obtaining_json(filename):
    """Obtains JSON file from different extentions"""
    if filename.endswith(".zip"):
        # Creates a list with all JSON within the extention
        json_files_list = []
        zip_file = zipfile.ZipFile(filename, "r")
        list_filenames = zip_file.namelist()
        if os.path.exists("test"):
            shutil.rmtree("test")
        os.mkdir("test", 0o666)
        for file in list_filenames:
            if file.endswith('.json'):
                # zip_file.extract(file)
                zip_file.extract(file, "test")
                json_files_list.append(file)
        zip_file.close()
        return json_files_list
    elif filename.endswith(".json"):
        json_file = json.loads(open(filename, encoding="utf8").read())
    elif filename.endswith(".sb3"):
        json_file = sb3_json_extraction(filename)
    return json_file


def main(filename, ignoring, json_content):
    """The main thread of execution for my software"""
    duplicateScripts.main(filename, json_content, ignoring)
    most_frequent_blocks.main(json_content)
    spritefile = filename.replace("." + filename.split(".")[1], '')\
        + '-sprite.json'
    projectfile = filename.replace("." + filename.split(".")[1], '')\
        + '-project.json'
    print("\n-- GETTING INTRA SPRITE STATISTICS --\n")
    statistics.main(json.loads(open(spritefile).read()))
    print("\n-- GETTING INTRA PROJECT STATISTICS --\n")
    statistics.main(json.loads(open(projectfile).read()))
    print("\n-- STARTING CLUSTER.PY SCRIPT --\n")
    cluster.main(json_content)
    print("\n-- END OF CLUSTER.PY SCRIPT --\n")
    os.remove(spritefile)
    os.remove(projectfile)
    os.remove(filename.split(".")[0] + '-custom.json')


def start(filename, ignoring):
    """The first steps to obtain information from filename"""
    print("\n*** STARTING ANALYSIS  ***\n")
    json_project = obtaining_json(filename)
    if filename.endswith('.zip'):
        # Still in need to be tested in multiple files
        # os.chdir("test")
        for i in json_project:
            print("\n---- OPENING FILE:", i, "  ----\n")
            os.chdir("test")
            json_file = json.loads(open(i, encoding="utf8").read())
            os.chdir("..")
            try:
                main(filename, ignoring, json_file)
            except duplicateScripts.NextFile:
                logging.info("FILE " + i + " HAS AN KEYERROR. CHECK DEEPLY")
                print("FILE: ", i, " HAS AN ERROR.")
                print("\n---- CLOSING FILE FROM ZIP ", i, "  ----\n")
                pass
    else:
        main(filename, ignoring, json_project)
    print("\n*** ENDING ANALYSIS ***\n")
    logging.info("Program works as expected.")


if __name__ == "__main__":
    logging.basicConfig(filename="program_logs.txt", level=logging.DEBUG,
                        format="%(asctime)s - %(levelname)s: %(message)s")
    try:
        if len(sys.argv) == 2:
            start(sys.argv[1], False)
        elif len(sys.argv) == 3 and str(sys.argv[2]) == "-i":
            print("\nYou are now ignoring blocks\n")
            start(sys.argv[1], True)
        else:
            raise IndexError
    except IndexError:
        logging.critical("Index Error: Number of arguments is not correct.")
        sys.exit("\nUsage: python3 duplicateScriptsApprox.py" +
                 " <file(.SB3 or .JSON or .ZIP)> [-i]\n" +
                 "\n-i (OPTIONAL): Ignore blocks from IgnoreBlocks.txt\n")
    except FileNotFoundError:
        logging.critical("File Not Found Error: " +
                         "File name does not exist or is not well written.")
        logging.critical(traceback.format_exc())
        sys.exit("\nPlease, use a file that exists in directory\n")
    except ModuleNotFoundError:
        logging.critical("Module Not Found Error:" +
                         "pip install -r requirements.txt")
        sys.exit("\nPlease, execute: pip install -r requirements.txt\n")
    except KeyboardInterrupt:
        logging.critical("User endend execution.")
        sys.exit("\nExecution interrupted by keyboard. Goodbye.\n")
    except:
        logging.critical(traceback.format_exc())
        sys.exit("\nSomething unexpected happened. " +
                 "Check errors in file program_logs.txt")
