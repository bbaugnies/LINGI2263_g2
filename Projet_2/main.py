#!/usr/local/bin/python3

__author__ = """ Martin Crochelet And Benjamin Baugnies """

from tags_and_words_statistics import CorpusParser

parser = CorpusParser()

parser.parse_file()
parser.build_lexicon()
parser.sort_tags()
parser.lexiconize_files()

print('-------------------------------------------------------------------------------------------------------')
print('  Further Data:')
print('-------------------------------------------------------------------------------------------------------')

print('\tThe 10 most frequent "words" in the train file are: (in order) \n\t\t', [word[1] for word in parser.frequent_words[-10:]])
print('\tThe 10 most frequent "tags" in the train file are: (in order)  \n\t\t', parser.tags[-10:])
print('\tThe 10 least frequent "tags" in the train file are: (in order) \n\t\t', parser.tags[:10])

parser.close_parser()


