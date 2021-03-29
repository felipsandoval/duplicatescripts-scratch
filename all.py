import duplicateScriptsApprox
import statistics
import cluster
import sys
from os import walk

from datetime import datetime
startTime = datetime.now()

cluster.main("all-project.json")

print(datetime.now() - startTime)


#mypath = sys.argv[1]
#_, _, filenames = next(walk(mypath))
#for filename in filenames:
#    duplicateScriptsApprox.main(mypath + filename)
    #statistics.main(filename + "-intra.json")
    #statistics.main(filename + "-project.json")
#    cluster.main(mypath + filename.replace(".json", "") + "-project.json")