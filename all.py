import duplicateScriptsApprox
import statistics
import cluster
import sys

filename = sys.argv[1]

duplicateScriptsApprox.main(filename)
statistics.main(filename + "-intra.json")
statistics.main(filename + "-project.json")
cluster.main(filename + "-intra.json")
cluster.main(filename + "-project.json")