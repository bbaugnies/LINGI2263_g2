#!/usr/local/bin/python3

__author__ = """ Martin Crochelet And Benjamin Baugnies """

from tags_and_words_statistics import CorpusParser

parser = CorpusParser()

parser.parseFile()

fWords = parser.getMostFrequent(5)

print(fWords)

parser.closeParser()
