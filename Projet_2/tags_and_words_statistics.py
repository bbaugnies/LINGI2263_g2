# INGI2263 - Natural Language Processing: Assignment 2
# Tags and Word Statistics Maker:
# Uses the file brown_training to compute several statistics about the words and
# tags passed in arguments.

__author__ = """ Martin Crochelet And Benjamin Baugnies """
from datetime import datetime


class CorpusParser:

	def __init__(self):
		self.word_frequencies = {}
		self.tag_frequencies = {}

		self.file = open('brown_train', 'r')

		self.frequent_words = []
		self.frequent_tags = []
		self.lexicon = []
		self.tags = []

	def parse_file(self):
		print('-------------------------------------------------------------------------------------------------------')
		print('  Parsing the file training file: brown_train')
		print('-------------------------------------------------------------------------------------------------------')
		now = datetime.now()

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

				if tag not in self.tag_frequencies.keys():
					self.tag_frequencies[tag] = 0

				self.tag_frequencies[tag] += 1

		self.file.seek(0)
		print('elapsed time = ' + str((datetime.now() - now).total_seconds()) + ' s')

	def get_most_frequent(self, n=5000):
		if not self.frequent_words:
			# find the n largest elements
			for word in self.word_frequencies.keys():
				self.frequent_words.append((self.word_frequencies[word]['count'], word))

			self.frequent_words = sorted(self.frequent_words, key=lambda w: w[0])[-n:]
		return self.frequent_words

	def sort_tags(self):
		print('-------------------------------------------------------------------------------------------------------')
		print('  Sorting the tags from the in ram data structure')
		print('-------------------------------------------------------------------------------------------------------')
		now = datetime.now()
		if not self.tags:
			for tag in self.tag_frequencies.keys():
				self.frequent_tags.append((self.tag_frequencies[tag], tag))

			self.tags = sorted(self.frequent_tags, key=lambda t: t[0])
		print('elapsed time = ' + str((datetime.now() - now).total_seconds()) + ' s')
		return self.tags

	def build_lexicon(self, n=5000):
		print('-------------------------------------------------------------------------------------------------------')
		print('  Creating the lexicon from the in ram data structure')
		print('-------------------------------------------------------------------------------------------------------')
		now = datetime.now()
		if not self.lexicon:
			self.lexicon = [word[1] for word in self.get_most_frequent(n)]
		print('elapsed time = ' + str((datetime.now() - now).total_seconds()) + ' s')
		return self.lexicon

	def lexiconize_files(self):
		print('-------------------------------------------------------------------------------------------------------')
		print('  Trim the train and test files from the unknown words (that does not belong to the lexicon)')
		print('-------------------------------------------------------------------------------------------------------')
		now = datetime.now()
		lexicon = set(self.lexicon)  # because set lookup is really more efficient (10x faster! and the lexicon is a set anyway)
		legit_tags = set(self.tags)
		number_of_segments = 0
		number_of_tokens = 0
		tokens = set()
		# remove any word from the training file that is not in the lexicon
		lexiconized_file = open('lexiconized_brown_train', 'w')
		for segment in self.file:
			number_of_segments += 1
			segment = segment.rstrip('\n')
			for token in segment.split(' '):        # split the line into the different tokens
				tokens.add(token)
				number_of_tokens += 1
				[word, tag] = token.rsplit('/', 1)  # split the WORD/TAG token by splitting at the last occurence of '/'

				if word in lexicon:
					lexiconized_file.write(token+' ' if tag != '.' else token+'')
				else:
					lexiconized_file.write('<UNK>/'+tag+' ' if tag != '.' else '<UNK>/'+tag)
			lexiconized_file.write('\n')
		lexiconized_file.close()
		print('\tnumber of types in train file = ' + str(len(tokens)))
		print('\tnumber of tokens in train file = ' + str(number_of_tokens))
		print('\tnumber of segments in train file = ' + str(number_of_segments))


		# do the same for the test file:
		lexiconized_file = open('lexiconized_brown_test', 'w')
		test_file = open('brown_test', 'r')
		number_of_segments = 0
		number_of_tokens = 0
		tokens = set()

		for segment in test_file:
			number_of_segments += 1
			segment = segment.rstrip('\n')
			for token in segment.split(' '):        # split the line into the different tokens
				[word, tag] = token.rsplit('/', 1)  # split the WORD/TAG token by splitting at the last occurence of '/'
				number_of_tokens += 1
				if word in lexicon:
					if tag is legit_tags:
						lexiconized_file.write(token + ' ' if tag != '.' else token + '')
						tokens.add(token)
					else:
						lexiconized_file.write(word+'/<UNK> ' if tag != '.' else word+'/<UNK>')
						tokens.add(word+'/<UNK>')
				else:
					if tag is legit_tags:
						lexiconized_file.write('<UNK>/'+tag+' ' if tag != '.' else '<UNK>/'+tag)
						tokens.add('<UNK>/'+tag)
					else:
						lexiconized_file.write('<UNK>/<UNK> ' if tag != '.' else '<UNK>/<UNK>')
						tokens.add('<UNK>/<UNK>')
			lexiconized_file.write('\n')
		lexiconized_file.close()
		print('\n\tnumber of types in test file = ' + str(len(tokens)))
		print('\tnumber of tokens in test file = ' + str(number_of_tokens))
		print('\tnumber of segments in test file = '+ str(number_of_segments))
		print('elapsed time = ' + str((datetime.now() - now).total_seconds()) + ' s')

	def close_parser(self):
		self.file.close()
