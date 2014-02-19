#!/usr/local/bin/python3

## imports
from io import SEEK_END, SEEK_SET
from exporter import Exporter
import math
import re

re.IGNORECASE = True

# utilities regex's
float_string = r'(\d+(\.\d*)?|\.\d)'
days    = re.compile(r'days?')
weeks   = re.compile(r'weeks?')
months  = re.compile(r'months?')
years   = re.compile(r'years?')
number  = re.compile(float_string)


# age
age     = [re.compile(r' '+float_string+r'[ -](years?)?(months?)?(weeks?)?(days?)?[ -]old'),
           re.compile(float_string+r' y/o '),
           re.compile(float_string+r' (years)?(months)? of age')]
# gender
female  = re.compile(r' girl | woman | female | lady ')
male    = re.compile(r' boy | man | male ')

# weight
weight  = re.compile(r'weigh[st] [^.]*'+float_string+' (pounds?|kilos?|kg)')

# temperature
temp    = re.compile(r'([tT]emperature(:)?(\n)?( )?(\n)?((\w+ ){,5})(\n)?(\d+(\.\d*)?|\.\d))' +
                     r'|' +
                     r'(((\d+(\.\d*)?|\.\d) ([dD]egrees )?([fF]ahrenheit )?[tT]emperature)(?!((\n)?(:)?( is )?)))')


class TranscriptGen:
    k = 0
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
        num = float(number.search(matches[0][1].group()).group())

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


def getTemp(transcript):
    matches = temp.search(transcript)
    if matches is None:
        return 'NA'
    else:
        m = matches.group()
        print('m', m)
        t = number.search(m).group()
        print(t)
        t = float(t)
        if t > 45:  # corporal temperature way above lethal one in Celsius!
            return round((t - 32.0) * 5.0/9.0, 2)
        return t



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
    temperature = str(getTemp(transcript))
    if temperature != 'NA':
        TranscriptGen.k +=1
    exp.addToTable(numb=str(i),  gender=get_gender(transcript), age=str(get_age(transcript)), bodyTemp=temperature)
    i += 1
print(TranscriptGen.k)
exp.write()