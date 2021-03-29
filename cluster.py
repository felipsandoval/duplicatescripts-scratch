#!/usr/bin/python3.8
import numpy as np
from sklearn.cluster import AffinityPropagation
import distance
from collections import Counter
from statistics import json2dna
import sys

def main (filename):
    (scripts, blocks_dict) = json2dna(filename)
    if not scripts:
        return None
    c = Counter(tuple(scripts))

    # Affinity propagation clustering
    # Taken from https://stats.stackexchange.com/questions/123060/clustering-a-long-list-of-strings-words-into-similarity-groups
    words = list(set(scripts))
    words = np.asarray(words)  # So that indexing with a list will work
    lev_similarity = -1 * np.array([[distance.levenshtein(w1, w2) for w1 in words] for w2 in words])

    affprop = AffinityPropagation(affinity="precomputed", damping=0.75, random_state=None)
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