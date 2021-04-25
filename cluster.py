#!/usr/bin/python3.8
from collections import Counter
from statistics import json2dna
import sys
import subprocess
import sys
from pip._internal import main as pip
import sklearn
try:
    import numpy as np
except ImportError:
    pip(['install', '--user', 'numpy'])
    import numpy as np
try:
    import distance
except ImportError:
    pip(['install', '--user', 'distance'])
    import distance
#try:
#    from sklearn.cluster import AffinityPropagation
#except ImportError:
#    pip(['install', '--user', 'scikit-learn'])
#    pip(['install', '--user', 'sklearn.cluster'])
#    pip(['install', '--user', 'spicy'])
#    pip(['install', '--user', 'matplotlib'])
#    from sklearn.cluster import AffinityPropagation

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main (filename):
    (scripts, blocks_dict) = json2dna(filename)
    if not scripts:
        return None
    c = Counter(tuple(scripts))

    # Affinity propagation clustering
    # Taken from https://stats.stackexchange.com/questions/123060/clustering-a-long-list-of-strings-words-into-similarity-groups
    words = list(set(scripts))
    #print(words)
    words = np.asarray(words)  # So that indexing with a list will work
    lev_similarity = -1 * np.array([[distance.levenshtein(w1, w2) for w1 in words] for w2 in words])

    affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.75, random_state=None)
    affprop.fit(lev_similarity)
    for cluster_id in np.unique(affprop.labels_):
        exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
        cluster = np.unique(words[np.nonzero(affprop.labels_ == cluster_id)])
        sum_all = sum([c[element] for element in cluster])
        cluster = [element + " (" + str(c[element]) + ")" for element in cluster]
        cluster_str = ", ".join(cluster)
        print("%s -- *%s (%s):* %s" % (sum_all, exemplar, c[exemplar], cluster_str))
    print()

if __name__ == "__main__":
    main(sys.argv[1])