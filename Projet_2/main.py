#!/usr/local/bin/python3

__author__ = """ Martin Crochelet And Benjamin Baugnies """

from tags_and_words_statistics import CorpusParser

parser = CorpusParser()

parser.parse_file()

a=parser.build_lexicon()

parser.lexiconize_files()

parser.report_words_tags(10)

parser.close_parser()


