#!/usr/local/bin/python3
from io import SEEK_END, SEEK_SET

import re
age = [re.compile(' \d+[ -](years?)?(months?)?(weeks?)?(days?)?[ -]old'), re.compile('\d+ y/o '), re.compile('\d+ (years)?(months)? of age')]
days = re.compile('days?')
weeks = re.compile('weeks?')
months = re.compile('months?')
years = re.compile('years?')

female = re.compile(' girl | woman | female | lady ')
male = re.compile(' boy | man | male ')

weight = re.compile('weigh[st] [^.]*\d+ (pounds?|kilos?|kg)')

number = re.compile('\d+')


class TranscriptGen:
    def __init__(self, file):
        self.fo = open(file, 'r', encoding='utf-16')
        self.tran = ''
        self.line = self.fo.readline()
    

    def extract(self):

        # get the number of lines in the file
        pos = self.fo.tell()
        self.fo.seek(0, SEEK_END)
        end = self.fo.tell()
        self.fo.seek(pos, SEEK_SET)

        # allow a little bit of flexibility: 5 blank lines at the end of the file
        while end-pos >= 5:

            while self.line != '<transcript_end>\n':
                self.tran += self.line
                self.line = self.fo.readline()

            yield self.tran

            self.tran = ''
            self.line = self.fo.readline()

            pos = self.fo.tell()

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
	if m == None and f != None:
		return 'female'
	elif f == None and m != None:
		return 'male'
	elif f != None and m != None:
		if m.start()<f.start():
			return 'male'
		else:
			return 'female'
	else:
		return '-'


p = TranscriptGen('medical_transcripts.txt')
s = p.extract()
transcript = next(s)

try:
    while transcript != '':
        print(get_age(transcript), ' ',  get_gender(transcript))
        transcript = next(s)

except StopIteration:
    print('done')
finally:
    del p
    del s
    del transcript
