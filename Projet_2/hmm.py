#!/usr/local/bin/python3

__author__ = 'martincrochelet'


from tags_and_words_statistics import CorpusParser

parser = CorpusParser()

parser.parse_file()

parser.build_lexicon()

parser.build_HMM_matrixes()

parser.HMM_tag_file()