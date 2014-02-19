#!/usr/local/bin/python3

## imports
from io import SEEK_END, SEEK_SET
from exporter import Exporter
import math
import re

# creation of the regex's for the age:
age = [re.compile(' \d+[ -](years?)?(months?)?(weeks?)?(days?)?[ -]old'), re.compile('\d+ y/o '), re.compile('\d+ (years)?(months)? of age')]
days = re.compile('days?')
weeks = re.compile('weeks?')
months = re.compile('months?')
years = re.compile('years?')

# creation of the regex's fur the gender
female = re.compile(' girl | woman | female | lady ')
male = re.compile(' boy | man | male ')

# creation of the regex's for the weight
weight = re.compile('weigh[st] [^.]*\d+ (pounds?|kilos?|kg)')

# creation of the regex's for a number
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
    # searches for any appearances of the keywords associated to the age
    for re in age:
        m = re.search(s)
        if m is not None:
            matches += [(m.start(), m)]
    matches.sort()

    # only analyze the first occurence of any keyword
    if matches:
        first = matches[0][1].group()
        num = number.search(matches[0][1].group()).group()

        if days.search(first) is not None:
            return math.floor(num/365)
        elif months.search(first) is not None:
            return math.floor(num/12)
        elif weeks.search(first) is not None:
            return math.floor(num/52)
        else:
            return num
    else:
        return 'NA'


def get_gender(s):
    m = male.search(s)
    f = female.search(s)
    if m is None and f is not None:
        return 'Female'
    elif f is None and m is not None:
        return 'Male'
    elif f is not None and m is not None:
        if m.start() < f.start():
            return 'Male'
        else:
            return 'Female'
    else:
        return 'NA'


p = TranscriptGen('medical_transcripts.txt')
transcripts = p.extract()

exp = Exporter(Exporter.finemode)
i = 1
for transcript in transcripts:
    exp.addToTable(i, get_gender(transcript), get_age(transcript), 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA')
    i += 1

exp.write()