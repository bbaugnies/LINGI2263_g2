# INGI2263 - Natural Language Processing: Assignment 2
# Tags and Word Statistics Maker:
# Uses the file brown_training to compute several statistics about the words and
# tags passed in arguments.

__author__ = """ Martin Crochelet And Benjamin Baugnies """
from heapq import heappush, heappop, heapify
from datetime import datetime

class CorpusParser:

	def __init__(self):
		self.word_frequencies = {}
		self.file = open('brown_train', 'r')
		self.word_heap = []
		self.frequent_words = []
		self.lexicon = []

	def parse_file(self):
		print('-------------------------------------------------------------------------------------------------------')
		print('  Parsing the file training file: brown_train')
		print('-------------------------------------------------------------------------------------------------------')
		now = datetime.now()
		heapify(self.word_heap)

		for segment in self.file:
			segment = segment.rstrip('\n')
			for token in segment.split(' '):        # split the line into the different tokens
				[word, tag] = token.rsplit('/', 1)  # split the WORD/TAG token by splitting at the last occurence of '/'

				# update the dictionary containing the counts for the current word
				if word not in self.word_frequencies.keys():
					self.word_frequencies[word] = {}
					self.word_frequencies[word][tag] = 1
					self.word_frequencies[word]['count'] = 0
				elif tag not in self.word_frequencies[word].keys():
					self.word_frequencies[word][tag] = 1
				else:
					self.word_frequencies[word][tag] += 1

				self.word_frequencies[word]['count'] += 1

		for word in self.word_frequencies.keys():
			heappush(self.word_heap, (-self.word_frequencies[word]['count'], word))

		self.file.seek(0)
		print('elapsed time = ' + str((datetime.now() - now).total_seconds()) + ' s')

	def get_most_frequent(self, n=5000):
		if not self.frequent_words:
			# find the n largest elements
			for i in range(n):
				self.frequent_words.append(heappop(self.word_heap))
			# restore the heap state
			for tup in self.frequent_words:
				heappush(self.word_heap, tup)

		return self.frequent_words

	def build_lexicon(self, n=5000):
		print('-------------------------------------------------------------------------------------------------------')
		print('  Creating the lexicon from the in ram data structure')
		print('-------------------------------------------------------------------------------------------------------')
		now = datetime.now()
		if not self.lexicon:
			# because set lookup is really more efficient (10x faster! and the lexicon is a set anyway)
			self.lexicon = set([word[1] for word in self.get_most_frequent(n)])
		print('elapsed time = ' + str((datetime.now() - now).total_seconds()) + ' s')
		return self.lexicon

	def lexiconize_files(self):
		print('-------------------------------------------------------------------------------------------------------')
		print('  Trim the train and test files from the unknown words (that does not belong to the lexicon)')
		print('-------------------------------------------------------------------------------------------------------')
		now = datetime.now()

		# remove any word from the training file that is not in the lexicon
		lexiconized_file = open('lexiconized_brown_train', 'w')
		for segment in self.file:
			segment = segment.rstrip('\n')
			for token in segment.split(' '):        # split the line into the different tokens
				[word, tag] = token.rsplit('/', 1)  # split the WORD/TAG token by splitting at the last occurence of '/'

				if word in self.lexicon:
					lexiconized_file.write(token+' ' if tag != '.' else token+'')
				else:
					lexiconized_file.write('<UNK>/<UNK>'+' ' if tag != '.' else '<UNK>/<UNK>')
			lexiconized_file.write('\n')
		lexiconized_file.close()

		# do the same for the test file:
		lexiconized_file = open('lexiconized_brown_test', 'w')
		test_file = open('brown_test', 'r')
		for segment in test_file:
			segment = segment.rstrip('\n')
			for token in segment.split(' '):        # split the line into the different tokens
				[word, tag] = token.rsplit('/', 1)  # split the WORD/TAG token by splitting at the last occurence of '/'

				if word in self.lexicon:
					lexiconized_file.write(token + ' ' if tag != '.' else token + '')
				else:
					lexiconized_file.write('<UNK>/<UNK>' + ' ' if tag != '.' else '<UNK>/<UNK>')
			lexiconized_file.write('\n')
		lexiconized_file.close()

		print('elapsed time = ' + str((datetime.now() - now).total_seconds()) + ' s')

	def close_parser(self):
		self.file.close()
