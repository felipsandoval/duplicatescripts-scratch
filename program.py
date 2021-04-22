#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Made by Felipe E. Sandoval Sibada

import duplicateScriptsApprox
import statistics
import cluster
import most_frequent_blocks
import sys
from os import walk
from datetime import datetime

#startTime = datetime.now()

#cluster.main("project.json")

#print(datetime.now() - startTime)

#mypath = sys.argv[1]
#_, _, filenames = next(walk(mypath))
#for filename in filenames:
#    duplicateScriptsApprox.main(mypath + filename)
    #statistics.main(filename + "-intra.json")
    #statistics.main(filename + "-project.json")
#    cluster.main(mypath + filename.replace(".json", "") + "-project.json")

def main(filename, ignoring):
    """MAIN PROGRAM"""
    duplicateScriptsApprox.main(filename, ignoring)
    most_frequent_blocks.main(filename)
    spritefile = filename.replace('.json', '') + '-sprite.json'
    projectfile = filename.replace('.json', '') + '-project.json'
    print("\n-- INTRA SPRITE STATISTICS --\n")
    statistics.main(spritefile)
    print("\n-- INTRA PROJECT STATISTICS --\n")
    statistics.main(projectfile)

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