#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

import argparse
import os
import string
import subprocess
from time import time

### This script prepares the network for embedding. It adds in the herb
### combination data in addition to the herb-symptom dictionary data.

# Records the set of nodes already written to file. Also unique number of edges.
global_node_set, global_node_types = set([]), {}
global_edge_set, num_edge_types = set([]), 0

def read_herb_combo_data():
    '''
    Returns a set of herb-herb edges. An edge is formed if its two nodes appear
    in the same herb combination.
    '''
    def parse_herb(herb):
        '''
        Gets the stripped version of the herb name.
        '''
        new_herb = ''
        for char in herb.decode('utf-8'):
            if u'\u4e00' > char or char > u'\u9fff':
                break
            new_herb += char
        return ''.join(new_herb).encode('utf-8')

    herb_combo_edge_set = set([])
    f = open('./data/herb_combo_data.txt', 'r')
    for line in f:
        line = line.strip().split('\t')
        assert len(line) == 2
        # Herbs are the second list. Replace Chinese commas with English commas.
        herb_lst = line[1]
        herb_lst = herb_lst.replace('、', ',').replace('，', ',').replace('。', '')
        herb_lst = herb_lst.split(',')

        # Parse individual herbs to remove dosages and footnotes.
        parsed_herb_set = set([])
        for herb in herb_lst:
            parsed_herb = parse_herb(herb)
            if parsed_herb != '':
                parsed_herb_set.add(parsed_herb)

        # Get neighbors for each combination.
        for herb in parsed_herb_set:
            # Update each herb with all other herbs in the list.
            for neighbor in parsed_herb_set - set([herb]):
                herb_combo_edge_set.add((herb, neighbor))
    f.close()
    return herb_combo_edge_set

def get_dictionary_symptom_herb_set():
    '''
    Returns a list of (symptom, herb) tuples.
    '''
    symptom_herb_set = set([])

    f = open('./data/herb_symptom_dictionary.txt', 'r')
    f.readline() # Skip header line.
    for line in f:
        line = line.strip().split('\t')

        line_length = len(line)
        # Some symptoms don't have good English translations.
        assert line_length == 2 or line_length == 5
        if line_length == 2:
            herb, symptom = line
        elif line_length == 5:
            herb, symptom, english_symptom, db_src, db_src_id = line
        # Special herb cases.
        if '(' in herb:
            herb = herb[:herb.index('(')]
        elif '银翘片' in herb:
            herb = '银翘片'
        # Reformatting potential bad strings.
        symptom = symptom.replace('/', '_').replace(' ', '_')
        herb = herb.replace('/', '_').replace(' ', '_')
        symptom_herb_set.add((symptom, herb))
    f.close()
    return symptom_herb_set

def write_edges(edge_out, edge_set, node_type_tup):
    '''
    Write the edges out to file. edge_label is just a letter to differentiate
    amongst the different types of edges. We write nodes out as integers, so
    map_out contains a word on each line corresponding to these integers.
    '''
    global global_node_set, global_edge_set, global_node_types, num_edge_types

    edge_label = string.ascii_lowercase[num_edge_types]
    for edge in edge_set:
        # Check if edge has already been written.
        if edge in global_edge_set or edge[::-1] in global_edge_set:
            continue
        global_edge_set.add(edge)

        # Write out the edge.
        for i in range(2):
            global_node_set.add(edge[i])
            global_node_types[edge[i]] = node_type_tup[i]
            edge_out.write('%s\t%s\t1\t%s\n' % (edge[i], edge[1 - i], edge_label))
    num_edge_types += 1

def write_nodes():
    node_out = open('./data/prosnet_inputs/%s' % node_fname, 'w')
    for node in global_node_set:
        node_out.write('%s\t%s\n' % (node, global_node_types[node]))
    node_out.close()

def run_prosnet():
    os.chdir('../prosnet')
    input_folder = '../herb_combinations/data/prosnet_inputs'

    out_folder = '../herb_combinations/data/prosnet_vectors'
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    command = ('./embed -node %s/%s -link %s/%s -meta_path %s/meta.txt -output '
        '%s/prosnet_vectors_%s_%s_%s -binary 0 -size %s '
        '-negative 5 -samples 1 -iters 11 -threads 24 -model 2 -depth 10 '
        '-restart 0.8 -edge_type_num %d -train_mode 2' % (input_folder, node_fname,
            input_folder, edge_fname, input_folder, out_folder, time(), args.num_dim,
            # args.num_dim, num_edge_types + 1))
            args.emr, args.num_dim, num_edge_types))
    print command
    subprocess.call(command, shell=True)

def parse_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--num_dim', help='number of ProSNet dimensions',
        required=True, type=int)
    parser.add_argument('-e', '--emr', required=True, choices=['true', 'false'],
        help='whether to include EMR data')
    args = parser.parse_args()

def main():
    parse_args()

    herb_combo_edge_set = read_herb_combo_data()
    symptom_herb_set = get_dictionary_symptom_herb_set()

    # Create the folder and files for the ProSNet input network.
    input_folder = './data/prosnet_inputs'
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)

    global edge_fname, node_fname
    edge_fname = 'prosnet_edge_list_%s.txt' % args.emr
    node_fname = 'prosnet_node_list_%s.txt' % args.emr
    edge_out = open('%s/%s' % (input_folder, edge_fname), 'w')
    write_edges(edge_out, herb_combo_edge_set, ('h', 'h'))
    write_edges(edge_out, symptom_herb_set, ('s', 'h'))
    edge_out.close()

    write_nodes()
    run_prosnet()

if __name__ == '__main__':
    main()