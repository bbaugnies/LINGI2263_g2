#!/usr/local/bin/python3

## imports
from io import SEEK_END, SEEK_SET
from exporter import Exporter
import math
import re
import string
import sys
import argparse

#---------------------------------------
# Regular expression definition


re.IGNORECASE = True

# utilities regex's
float_string = r'(\d+(\.\d*)?|\.\d)'
fraction = r'\d+(((-and-)?|-)(\d+/\d+|a-half))?'
eow = r'(\s|['+string.punctuation+'])'
days    = re.compile(r'days?')
weeks   = re.compile(r'weeks?')
months  = re.compile(r'months?')
years   = re.compile(r'years?')
pounds = re.compile(r'pounds?')
kilos = re.compile(r'kg|kilo(gram)?s?'+eow)
feet = re.compile(r"f[eo]{2}t|'")
inches = re.compile(r'inch(es)?|"')
number  = re.compile(float_string)


# age
age     = re.compile(r'('+float_string+'|'+fraction+')('
          r'[ -](years?)?(months?)?(weeks?)?(days?)?[ -]old|'+
          r'\sy/o\s|'+
          r'\s(years)?(months)? of age)')
# gender
female = re.compile(r'(\sgirl|woman|female|\slady|Mrs.|Ms.)'+eow)
male = re.compile(r'(\sboy|\sman|\smale|Mr.|gentleman)'+eow)


# For weight and height, lists of regex set a priority
# (prefer a mention to weight/height to an isolated value)

# weight
weightexpr = r'\d+[.]?\d*\s(pounds?|kilo(gram)?s?(\s|['+string.punctuation+'])|kg)'
weight     = [re.compile(r'(weigh[st]|([wW][tT]))[^.]{,5}'+weightexpr+'|'+
                      weightexpr+'[^.]{,5}weight'), 
           re.compile(weightexpr)]

# height
length = (float_string+'\s?cm|'+
          '\d+\s?f[eo]{2}t(\s?'+fraction+'\s?inch(es)?)?|'+
          fraction+"\s?inch(es)?|"+
          fraction+"'\s?("+fraction+'\s?")?|'+
          fraction+'\s?"')
height = [re.compile(r'(height[^.]{,5}|ht([^a]|a){,5})'+length+'|'+
                     length+'[^.]{,5}(height|tall)'),
          re.compile(length)]

# BMI
bmi = re.compile(r"BMI[^.]{,5}"+float_string)

# Oxygen saturation
o2sat = 'o(2|xygen)\ssat(uration)?'
o2value = '\d+(-\d+)?%'
roomair = re.compile('room air[^.]'+o2sat+'[^.]*'+o2value+
                     '|'+o2sat+'[^.]*room air[^.]*'+o2value+
                     '|'+o2sat+'[^.]*'+o2value+'[^.]*room air')
ambulation = re.compile('ambulation[^.]'+o2sat+'[^.]*'+o2value+
                     '|'+o2sat+'[^.]*ambulation[^.]*'+o2value+
                     '|'+o2sat+'[^.]*'+o2value+'[^.]*ambulation')
o2no_con = re.compile(o2sat+'[^.]*'+o2value)


# temperature
temp    = re.compile(r'([tT]emperatures?( )?:?\n?( )?\n?(([a-zA-Z]+ ?){,5}?)?\n?( )?(\d+(\.\d*)?|\.\d))' +
                     r'|' +
                     r'(\b((T)|(TEMP)|([tT]emp))\b:?\n? (\d+(\.\d*)?|\.\d))' +
                     r'|' +
                     r'(((\d+(\.\d*)?|\.\d) (([a-zA-Z]+ ?){,3}?)?[tT]emperature)(?!((([a-zA-Z]+ ?){,2}?)?\n?( )?(\d+(\.\d*)?|\.\d))))')

pulse   = re.compile(r'((([pP]ulses?)|([hH]eart rate)):?\n?( )?\n?(([a-zA-Z]+ ?){,3}?)?\n?( )?(\d+(\.\d*)?|\.\d))'+
                     r'|' +
                     r'(\b(P|([hH][rR]))\b:?\n? (\d+(\.\d*)?|\.\d))')

breath  = re.compile(r'([rR]espiratory rate\n?( )?\n?:?\n?(([a-zA-Z]+ ?){,3}?)?\n?( )?(\d+(\.\d*)?|\.\d))' +
                     r'|' +
                     r'(\bRR\b:?\n? (\d+(\.\d*)?|\.\d))')

bloodP  = re.compile('((([bB]lood [pP]ressure)|([bB][pP]))( )?:?\n?( )?\n?(([a-zA-Z]+ ?){,3}?)?\n?( )?((\d+(\.\d*)?|\.\d)/(\d+(\.\d*)?|\.\d)))')
#------------------------------------------------
# Utility functions/classes


# Computes a decimal value for various number formats
def getNumber(s):
    n = number.search(s)
    sub = s
    if n is None:
        print(s)
        return None
    res = float(n.group())
    sub=s[n.end():]
    if '/' in sub and 'y/o' not in sub:
        n = number.search(sub)
        numerator = 0
        if n != None:
            numerator = float(n.group())
            sub = sub[n.end():]
            n = number.search(sub)
            if n != None:
                denominator = float(n.group())
                return round(res+numerator/denominator, 2)
        else:
            return numerator
    elif 'half' in sub:
        return res+0.5
    else:
        return res


# Allows the extraction of individual transcripts
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

#-------------------------------------------------
# Data extraction methods


# Extract the patient's age
# Supposes the first mentionned age is most likely to be the patient's
# does not cover fully typed out numbers (e.g. 'two-and-a-half-year-old')
def getAge(transcript):
    m = age.search(transcript)
    if m is not None:
        num = getNumber(m.group())
        if days.search(m.group()) is not None:
            return round(num/365, 2)
        elif months.search(m.group()) is not None:
            return round(num/12, 2)
        elif weeks.search(m.group()) is not None:
            return round(num/52, 2)
        else:
            return num
    else:
        return 'NA'


# Extracts patient temperature
def getTemp(transcript):
    matches = temp.search(transcript)
    if matches is None:
        return 'NA'
    else:
        t = float(number.search(matches.group()).group())
        if t > 45:  # corporal temperature way above lethal one in Celsius!
            return round((t - 32.0) * 5.0/9.0, 2)
        return t


# Extracts patient pulse
def getPulse(transcript):
    matches = pulse.search(transcript)
    if matches is None:
        return 'NA'
    else:
        p = float(number.search(matches.group()).group())
        if 1 < p < 4:
            return 'normal'

        return p if p > 4 else 'NA'


# Extracts patient gender
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


# Extracts patient weight
def getWeight(s):
    # "arbitrary" minimum weight of 30kg for an adult:
    # many mentions of lifted weight (e.g: "lifting 40 pounds")
    # cause false results.
    a = getAge(s)
    if a != 'NA':
        a = a<18
    else: a = True

    for r in weight:
        w = r.search(s)
        if w is not None:
            break
    if w is not None:
        w = w.group()
        if pounds.search(w) is not None:
            w=round(float(number.search(w).group())/2.20462, 2)
            if a or w>=30:
                return w
            else:
                return 'NA'
        elif kilos.search(s) is not None:
            w=round(float(number.search(w).group()), 2)
            if a or w>=30:
                return w
            else:
                return 'NA'
    else :
        return 'NA'


# Extracts patient height
def getHeight(transcript):
    # "arbitrary" minimum height of 50cm for and adult
    a = getAge(transcript)
    if a != 'NA':
        a = a<18
    else: a = True

    for r in height:
        h = r.search(transcript)
        if h is not None:
            break
    if h is not None:
        h = h.group()
        if feet.search(h) is not None:
            if inches.search(h) is None:
                res = round(getNumber(h)/3.2808, 2)
            else:
                res = float(number.search(h).group())
                h = h[number.search(h).end():]
                res += getNumber(h)/12
                res = round(res/3.2808, 2)
        elif inches.search(h) is not None:
            res = round(getNumber(h)/12/3.2808, 2)
        else:
            res = round(getNumber(h)/100, 2)
        if a or  res >= 0.5:
            return res
        else:
            return 'NA'
    else:
        return 'NA'


# Extract patient BMI
def getBMI(transcript):
    b = bmi.search(transcript)
    if b is not None:
        b = b.group()
        return round(getNumber(b), 2)
    else:
        w = getWeight(transcript)
        if w != 'NA':
            h = getHeight(transcript)
            if h != 'NA' and h > 0.5:
                return round(w/pow(h, 2), 2)
            else:
                return 'NA'
        else:
            return 'NA'

            
#Extract patient O2sat
def getO2sat(transcript):
	o = roomair.search(transcript)
	if o is not None:
		return (getNumber(o.group()), 'room air')
	o = ambulation.search(transcript)
	if o is not None:
		return (getNumber(o.group()), 'ambulation')
	o = o2no_con.search(transcript)
	if o is not None:
		return (getNumber(o.group()), '(room air)')
	return ('NA', 'NA')
        

# Extracts patient breathing frequency
def getBreath(transcript):
    matches = breath.search(transcript)
    if matches is None:
        return 'NA'
    else:
        return float(number.search(matches.group()).group())


# Extracts patient breathing frequency
def getBloodP(transcript):
    matches = bloodP.search(transcript)
    if matches is None:
        return 'NA'
    else:
        frac = re.search('(\d+/\d+)', matches.group())
        # individual_numbers = re.findall('(\d+(\.\d*)?|\.\d)', frac.group())
        return frac.group()




#--------------------------------------------------
# data extraction

parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('output_file')
parser.add_argument('--fine', dest='mode', action='store_const', const=Exporter.finemode, default=Exporter.rawmode, 
                    help = 'sends output to output.html for better readability' )

arg = parser.parse_args()

p = TranscriptGen(arg.input_file)
transcripts = p.extract()

# default output is rawmode
exp = Exporter(arg.mode, arg.output_file)
i       = 0
bpcount = 0
gecount = 0
agcount = 0
tpcount = 0
pucount = 0
brcount = 0
wecount = 0
hecount = 0
bmcount = 0
o2count = 0
for transcript in transcripts:
    bp = str(getBloodP(transcript))
    ge = str(getGender(transcript))
    ag = str(getAge(transcript))
    tp = str(getTemp(transcript))
    pu = str(getPulse(transcript))
    br = str(getBreath(transcript))
    we = str(getWeight(transcript))
    he = str(getHeight(transcript))
    bm = str(getBMI(transcript))
    o2 = getO2sat(transcript)
    o2_cond = o2[1]
    o2 = str(o2[0])
    if bp != 'NA': bpcount += 1
    if ge != 'NA': gecount += 1
    if ag != 'NA': agcount += 1
    if tp != 'NA': tpcount += 1
    if pu != 'NA': pucount += 1
    if br != 'NA': brcount += 1
    if we != 'NA': wecount += 1
    if he != 'NA': hecount += 1
    if bm != 'NA': bmcount += 1
    if o2 != 'NA': o2count += 1
    exp.addToTable(numb=str(i),  gender=ge, age=ag, bodyTemp=tp, pulse=pu, breath=br, weight=we, height=he, bmi=bm,
                   bloodP=bp, o2sat=o2, o2cond=o2_cond)
    i += 1

exp.write()

print('=======================================================================================================================')
print('Hits : (percentage of transcripts where the information has been found)')
print('gender\t\t\t:',              round(gecount/i, 2)*100, '%')
print('age\t\t\t:',                 round(agcount/i, 2)*100, '%')
print('weight\t\t\t:',              round(wecount/i, 2)*100, '%')
print('height\t\t\t:',              round(hecount/i, 2)*100, '%')
print('bmi\t\t\t:',                 round(bmcount/i, 2)*100, '%')
print('body temperature\t:',        round(tpcount/i, 2)*100, '%')
print('pulse\t\t\t:',               round(pucount/i, 2)*100, '%')
print('breathing frequency\t:',     round(brcount/i, 2)*100, '%')
print('blood pressure\t\t:',        round(bpcount/i, 2)*100, '%')
print('oxygen saturation\t\t:',     round(o2count/i, 2)*100, '%')
print('=======================================================================================================================')
