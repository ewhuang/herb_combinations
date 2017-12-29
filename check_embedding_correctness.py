### Author: Edward Huang

import numpy as np
import operator
from sklearn.metrics.pairwise import cosine_similarity

### This script checks the correctess of the embedding vectors by outputting
### the most similar herb pairs via cosine similarity.


def read_input_file(fname):
    '''
    Reads the output low-dimensional vectors.
    '''
    feature_lst, vector_matrix = [], []
    f = open(fname, 'r')
    f.readline()
    for line in f:
        line = line.split()
        feature, vector = line[0], map(float, line[1:])
        feature_lst += [feature]
        vector_matrix += [vector]
    f.close()

    return feature_lst, np.array(vector_matrix)

def main():
    fname = './data/prosnet_vectors/prosnet_vectors_1513844093.99_500_false_10'
    feature_lst, vector_matrix = read_input_file(fname)

    similarity_matrix = np.abs(cosine_similarity(vector_matrix))

    print similarity_matrix.shape, vector_matrix.shape, len(feature_lst)
    # print ','.join(feature_lst)

    cos_dct = {}
    for a, element_a in enumerate(feature_lst):
        for b in range(a + 1, len(feature_lst)):
            cos_dct[(element_a, feature_lst[b])] = similarity_matrix[a][b]

    out = open('./data/top_herb_pairs.txt', 'w')
    sorted_cos_dct = sorted(cos_dct.items(), key=operator.itemgetter(1), reverse=True)[:100]
    for (element_a, element_b), val in sorted_cos_dct:
        out.write('%s\t%s\t%f\n'  % (element_a, element_b, val))

    out.close()

if __name__ == '__main__':
    main()