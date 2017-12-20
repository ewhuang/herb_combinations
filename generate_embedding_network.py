#!/usr/bin/python
# -*- coding: utf-8 -*-

### Author: Edward Huang

### This script prepares the network for embedding. It adds in the herb
### combination data in addition to the herb-symptom dictionary data.


def read_herb_combo_data():
	'''
	Returns a dictionary.
	Key: herb -> str
	Value: list of herbs that appear in the same combination as the key
		-> list(str)
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

	herb_neighbor_dct = {}
	f = open('./data/herb_combo_data.txt', 'r')
	for line in f:
		line = line.strip().split('\t')
		assert len(line) == 2
		# Herbs are the second list. Replace Chinese commas.
		herb_lst = line[1]
		herb_lst = herb_lst.replace('、', ',').replace('，', ',').replace('。', '')
		herb_lst = herb_lst.split(',')

		# Parse individual herbs to remove dosages and footnotes.
		parsed_herb_set = set([])
		for herb in herb_lst:
			parsed_herb_set.add(parse_herb(herb))

		# Get neighbors for each combination.
		for herb in parsed_herb_set:
			# Update each herb with all other herbs in the list.
			if herb not in herb_neighbor_dct:
				herb_neighbor_dct[herb] = set([])
			neighbor_set = parsed_herb_set - set([herb])
			herb_neighbor_dct[herb] = herb_neighbor_dct[herb].union(neighbor_set)
	f.close()
	return herb_neighbor_dct

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

def main():
	herb_neighbor_dct = read_herb_combo_data()

if __name__ == '__main__':
	main()