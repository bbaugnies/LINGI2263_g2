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
temp    = re.compile(r'([tT]emperatures?( )?:?\n?( )?\n?(([a-zA-Z]+ ?){,5}?)?\n?( )?(\d+(\.\d*)?|\.\d))' +
                     r'|' +
                     r'( ((T)|(TEMP)|([tT]emp)):?\n? (\d+(\.\d*)?|\.\d))' +
                     r'|' +
                     r'(((\d+(\.\d*)?|\.\d) ([dD]egrees )?([fF]ahrenheit )?[tT]emperature)(?!(\n?:?( is )?)))')

pulse   = re.compile(r'([pP]ulses?:?\n?( )?\n?(([a-zA-Z]+ ?){,3}?)?\n?( )?(\d+(\.\d*)?|\.\d))'+
                     r'|' +
                     r'( P:?\n? (\d+(\.\d*)?|\.\d))')

breath  = re.compile(r'([rR]espiratory rate\n?( )?\n?:?\n?(([a-zA-Z]+ ?){,3}?)?\n?( )?(\d+(\.\d*)?|\.\d))' +
                     r'|' +
                     r'( RR:?\n? (\d+(\.\d*)?|\.\d))')

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
def getAge(transcript):
    matches = []
    # searches for any appearances of the keywords associated to the age
    for re in age:
        m = re.search(transcript)
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
        t = float(number.search(matches.group()).group())
        if t > 45:  # corporal temperature way above lethal one in Celsius!
            return round((t - 32.0) * 5.0/9.0, 2)
        return t


def getPulse(transcript):
    matches = pulse.search(transcript)
    if matches is None:
        return 'NA'
    else:
        p = float(number.search(matches.group()).group())
        if 1 < p < 4:
            return 'normal'

        return p if p > 4 else 'NA'


def getGender(transcript):
    m = male.search(transcript)
    f = female.search(transcript)
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


def getBreath(transcript):
    matches = breath.search(transcript)
    if matches is None:
        return 'NA'
    else:
        return float(number.search(matches.group()).group())

p = TranscriptGen('medical_transcripts.txt')
transcripts = p.extract()

exp = Exporter(Exporter.finemode)
i = 1
for transcript in transcripts:
    p = str(getBreath(transcript))
    if p != 'NA':
        TranscriptGen.k += 1
    exp.addToTable(numb=str(i),  gender=getGender(transcript), age=str(getAge(transcript)),
                   bodyTemp=str(getTemp(transcript)), pulse=str(getPulse(transcript)), breath=str(getBreath(transcript)))
    i += 1
print(TranscriptGen.k)
exp.write()