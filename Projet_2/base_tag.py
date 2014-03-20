#!/usr/local/bin/python3

__author__ = """ Martin Crochelet And Benjamin Baugnies """

from tags_and_words_statistics import CorpusParser


#def find_best_tag(tags):
#	best_tags = {}
#	for word in tags:
#		count = 0
#		best = ''
#		del tags[word]['count']
#		for t in tags[word]:
#			if tags[word][t] > count:
#				count = tags[word][t]
#				best = t
#		best_tags[word]=best
#	return best_tags
			

parser = CorpusParser()

parser.parse_file()
#lexicon = parser.build_lexicon()
print('Number of tags: ', len(parser.tag_frequencies))
parser.word_frequencies['<UNK>']={'count':1, '<UNK>':1}

print('Stats for "THROUGH": ')
print(parser.word_frequencies['THROUGH'])

best_tags = parser.find_best_tag()


i_file= open('no_tag_brown_test', 'r')
o_file= open('base_tag_brown_test', 'w')
index = 0
for segment in i_file:
	index += 1
	segment = segment.rstrip('\n')
	for token in segment.split(' '): 
		if token != '' :
			o_file.write(token+'/'+best_tags[token]+' ')
	o_file.write('\n')

o_file.close()
i_file.close()

















