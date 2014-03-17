# INGI2263 - Natural Language Processing: Assignment 2
# Tags and Word Statistics Maker:
# Uses the file brown_training to compute several statistics about the words and
# tags passed in arguments.

__author__ = """ Martin Crochelet And Benjamin Baugnies """
from heapq import heappush, heappop, heapify


class CorpusParser:

	def __init__(self):
		self.wordFrequencies = {}
		self.file = open('brown_train', 'r')
		self.wordHeap = []
		self.frequentWords = []
		self.lexicon = []

	def parseFile(self):

		heapify(self.wordHeap)

		for segment in self.file:
			for token in segment.split(' '):        # split the line into the different tokens
				[word, tag] = token.rsplit('/', 1)  # split the WORD/TAG token by splitting at the last occurence of '/'

				# update the dictionary containing the counts for the current word
				if word not in self.wordFrequencies.keys():
					self.wordFrequencies[word] = {}
					self.wordFrequencies[word][tag] = 1
					self.wordFrequencies[word]['count'] = 0
				elif tag not in self.wordFrequencies[word].keys():
					self.wordFrequencies[word][tag] = 1
				else:
					self.wordFrequencies[word][tag] += 1

				self.wordFrequencies[word]['count'] += 1

		for word in self.wordFrequencies.keys():
			heappush(self.wordHeap, (-self.wordFrequencies[word]['count'], word))

	def getMostFrequent(self, n=5000):

		if not self.frequentWords:
			# find the n largest elements
			for i in range(n):
				self.frequentWords.append(heappop(self.wordHeap))

			# restore the heap state
			for tup in self.frequentWords:
				heappush(self.wordHeap, tup)

		return self.frequentWords

	def buildLexicon(self, n=5000):
		if not self.lexicon:
			self.lexicon = [word[1] for word in self.getMostFrequent(n)]
		return self.lexicon

	def closeParser(self):
		self.file.close()
