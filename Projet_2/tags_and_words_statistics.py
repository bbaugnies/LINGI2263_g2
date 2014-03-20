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

		self.transitivity_matrix = {}
		self.emitivity_matrix = {}
		self.epsilon = 0.001

	def find_best_tag(self):
		best_tags = {}
		for word in self.word_frequencies:
			count = 0
			best = ''
			del self.word_frequencies[word]['count']
			for t in self.word_frequencies[word]:
				if self.word_frequencies[word][t] > count:
					count = self.word_frequencies[word][t]
					best = t
			best_tags[word]=best
		return best_tags

	def build_HMM_matrixes(self):
		for tag in self.tag_frequencies.keys():
			for previous_tags in self.transitivity_matrix[tag].keys():
				self.transitivity_matrix[tag][previous_tags] = self.transitivity_matrix[tag][previous_tags] / self.tag_frequencies[tag]
		for word in self.lexicon:
			self.emitivity_matrix[word] = {}
			for tag in self.word_frequencies[word].keys():
				if tag != 'count':
					self.emitivity_matrix[word][tag] = self.word_frequencies[word][tag] / self.word_frequencies[word]['count']

		s = set(self.lexicon)
		self.emitivity_matrix['<UNK>'] = {}
		for word in self.word_frequencies.keys():
			if word not in s:
				for tag in self.word_frequencies[word].keys():
					if tag not in self.emitivity_matrix['<UNK>'].keys():
						self.emitivity_matrix['<UNK>'][tag] = 1
					else:
						self.emitivity_matrix['<UNK>'][tag] += 1


	def HMM_tag_file(self):
		file = open('no_tag_brown_test', 'r')
		out = open('HMM_tag_brown_test', 'w')

		for segment in file:
			segment = segment.rstrip('\n')
			word_sequence = segment.split(' ')
			tag_sequence = self.dfs_search(word_sequence)
			break
			for word, tag in zip(word_sequence, tag_sequence):
				out.write(word+'/'+tag+' ' if word != '.' else word+'/'+tag)

	def dfs_search(self, word_sequence):
		stack = []
		stack.append('<s>')

		def rec(wseq, stack):

			print(wseq[0])
			for tag in self.emitivity_matrix[wseq[0]]:
				stack.append(tag)
				rec(wseq[1:], stack)
			if len(wseq) == 0:
				val = self.evaluate_seq(stack, word_sequence)
				stack.pop()
				return val

		rec(word_sequence, stack)

	def evaluate_seq(self, seq, wseq):
		res = 1
		i = 1
		for word in wseq:
			if seq[i] not in self.emitivity_matrix[word].keys():
				return self.epsilon * self.epsilon
			if seq[i-1] not in self.transitivity_matrix[seq[i]].keys():
				res *= self.emitivity_matrix[word][seq[i]] * self.epsilon
			else:
				res *= self.emitivity_matrix[word][seq[i]] * self.transitivity_matrix[seq[i]][seq[i-1]]
			i += 1
		print(wseq, seq, res)
		return res

	def parse_file(self):
		print('-------------------------------------------------------------------------------------------------------')
		print('  Parsing the file training file: brown_train')
		print('-------------------------------------------------------------------------------------------------------')
		now = datetime.now()

		for segment in self.file:
			segment = segment.rstrip('\n')
			last_tag = '<s>'  # beginning of segment tag
			for token in segment.split(' '):        # split the line into the different tokens
				[word, tag] = token.rsplit('/', 1)  # split the WORD/TAG token by splitting at the last occurence of '/'

				if tag not in self.transitivity_matrix.keys():
					self.transitivity_matrix[tag] = {}
					self.transitivity_matrix[tag][last_tag] = 1
				elif last_tag not in self.transitivity_matrix[tag].keys():
					self.transitivity_matrix[tag][last_tag] = 1
				else:
					self.transitivity_matrix[tag][last_tag] += 1

				last_tag = tag

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
		print('\telapsed time = ' + str((datetime.now() - now).total_seconds()) + ' s')

	def get_most_frequent(self, n=5000):
		unique= 0 
		ucount = 0
		if not self.frequent_words:
			# find the n largest elements
			for word in self.word_frequencies.keys():
				self.frequent_words.append((self.word_frequencies[word]['count'], word))
				if len(self.word_frequencies[word]) == 2:
					unique += 1
					ucount += self.word_frequencies[word]['count']

			self.frequent_words = sorted(self.frequent_words, key=lambda w: w[0])[-n:]
		print('Number of uniquely tagged words: ', unique)
		print('Occurences of uniquely tagged words: ', ucount)
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
		print('\telapsed time = ' + str((datetime.now() - now).total_seconds()) + ' s')
		return self.tags

	def build_lexicon(self, n=5000):
		print('-------------------------------------------------------------------------------------------------------')
		print('  Creating the lexicon from the in ram data structure')
		print('-------------------------------------------------------------------------------------------------------')
		now = datetime.now()
		if not self.lexicon:
			self.lexicon = [word[1] for word in self.get_most_frequent(n)]
		print('\telapsed time = ' + str((datetime.now() - now).total_seconds()) + ' s')
		return self.lexicon

	def lexiconize_files(self):
		print('-------------------------------------------------------------------------------------------------------')
		print('  Trim the train and test files from the unknown words (that does not belong to the lexicon)')
		print('-------------------------------------------------------------------------------------------------------')
		now = datetime.now()
		lexicon = set(self.lexicon)  # because set lookup is really more efficient (10x faster! and the lexicon is a set anyway)
		legit_tags = set(tag[1] for tag in self.tags)
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
					lexiconized_file.write(token+' ' if word != '.' else token+'')
				else:
					lexiconized_file.write('<UNK>/'+tag+' ' if word != '.' else '<UNK>/'+tag)
			lexiconized_file.write('\n')
		lexiconized_file.close()
		print('\tnumber of types in train file = ' + str(len(tokens)))
		print('\tnumber of tokens in train file = ' + str(number_of_tokens))
		print('\tnumber of segments in train file = ' + str(number_of_segments))


		# do the same for the test file:
		lexiconized_file = open('lexiconized_brown_test', 'w')
		test_file = open('brown_test', 'r')
		#no_tag_file = open('no_tag_brown_test', 'w')
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
					if tag in legit_tags:
						lexiconized_file.write(token + ' ' if word != '.' else token + ' ')
						tokens.add(token)
					else:
						lexiconized_file.write(word+'/<UNK> ' if word != '.' else word+'/<UNK>')
						tokens.add(word+'/<UNK>')
					#no_tag_file.write(word + ' ')#if tag != '.' else word + '')
				else:
					if tag in legit_tags:
						lexiconized_file.write('<UNK>/<UNK> ' if word != '.' else '<UNK>/<UNK> ')
						tokens.add('<UNK>/'+tag)
					else:
						lexiconized_file.write('<UNK>/<UNK> ' if word != '.' else '<UNK>/<UNK>')
						tokens.add('<UNK>/<UNK>')
					#no_tag_file.write('<UNK>' + ' ' )#if tag != '.' else '<UNK>')


			#no_tag_file.write('\n')
			lexiconized_file.write('\n')
		lexiconized_file.close()
		print('\n\tnumber of types in test file = ' + str(len(tokens)))
		print('\tnumber of tokens in test file = ' + str(number_of_tokens))
		print('\tnumber of segments in test file = '+ str(number_of_segments))
		print('\telapsed time = ' + str((datetime.now() - now).total_seconds()) + ' s')

	def close_parser(self):
		self.file.close()
