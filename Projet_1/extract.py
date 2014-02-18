import re
age = [re.compile(' \d+[ -](years?)?(months?)?(weeks?)?(days?)?[ -]old'), re.compile('\d+ y/o '), re.compile('\d+ (years)?(months)? of age')]
days = re.compile('days?')
weeks = re.compile('weeks?')
months = re.compile('months?')
years = re.compile('years?')

female = re.compile(' girl | woman | female | lady ')
male = re.compile(' boy | man | male ')
number = re.compile('\d+')


class Transcript_gen:
	def __init__(self, file):
		self.fo = open(file, 'r', encoding='utf-16')
		self.tran = ''
		self.line = self.fo.readline()
	
	# not used, does not terminate loop correctly
	def extract(self):
		while self.line != '' :
			while self.line != '<transcript_end>\n' :
				self.tran += self.line
				self.line = self.fo.readline()
			yield self.tran
			self.tran = ''
			self.line = self.fo.readline()
		print('doneloop')

	# Returns next transcript
	def getnext(self):
		ntran = ''
		while (self.line!='<transcript_end>\n' and self.line != ''):
			ntran += self.line
			self.line = self.fo.readline()
		self.line = self.fo.readline()
		return ntran

# Supposes the first mentionned age is most likely to be the patient's
# does not cover fully typed out numbers (e.g. 'two-and-a-half-year-old')
def get_age(s):
	matches = []
	for re in age:
		m = re.search(s)
		if m != None:
			matches += [(m.start(), m)]
	matches.sort()
	if matches != []:
		first = matches[0][1].group()
		num = number.search(matches[0][1].group()).group()
		if days.search(first) != None :
			return num+' d'
		elif months.search(first) != None:
			return num + ' m'
		elif weeks.search(first) != None:
			return num + ' w'
		else:
			return num + ' y'
	else:
		return 'none'


def get_gender(s):
	m = male.search(s)
	f = female.search(s)
	if m == None:
		if f == None:
			return '-'
		else:
			return 'female'
	else:
		return 'male'


p = Transcript_gen('medical_transcripts.txt')
s = p.getnext()
while s != '':
	print(get_age(s)+ ' ' + get_gender(s))
	s= p.getnext()
