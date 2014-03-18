#!/usr/local/bin/python3

__author__ = """ Martin Crochelet And Benjamin Baugnies """

from tags_and_words_statistics import CorpusParser

parser = CorpusParser()

parser.parse_file()

parser.build_lexicon()

parser.lexiconize_files()

parser.close_parser()
