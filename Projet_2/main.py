#!/usr/local/bin/python3

__author__ = """ Martin Crochelet And Benjamin Baugnies """

from tags_and_words_statistics import CorpusParser

parser = CorpusParser()

parser.parse_file()
parser.build_lexicon()
parser.lexiconize_files()
parser.sort_tags()

print('\nThe 10 most frequent "words" in the train file are: (in order) \n', [word[1] for word in parser.frequent_words[-10:]], '\n')
print('\nThe 10 most frequent "tags" in the train file are: (in order) \n', parser.tags[-10:], '\n')
print('\nThe 10 least frequent "tags" in the train file are: (in order) \n', parser.tags[:10], '\n')

parser.close_parser()


