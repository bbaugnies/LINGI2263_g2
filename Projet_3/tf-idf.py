import string
import math

min_idf = 0
n_res = 20
query = ["school" , "book", "fruit", "house", "mayhem", "plane"]

fo = open("definitions-utf8.txt", "r")
dict = {}
words = {}
doc_count = 0
for i in fo:
	d = i.translate(string.maketrans("\t", " "), string.punctuation+'\n')
	d = d.lower()
	d = str.split(d, ' ')
	if len(d) > 1:
		doc_count += 1
		d_words = []
		for j in d[1:]:
			if j not in words:
				words[j] = 1
				d_words.append(j)
			else:
				if j not in d_words:
					words[j] += 1
					d_words.append(j)

for w in words:
	words[w] = math.log(words[w]/float(doc_count))*(-1)
print(len(words), " ", doc_count)

fo.seek(0)


def sim(d1, d2):
	prod = 0
	for w in d1[0]:
		if w in d2[0]:
			prod+= d1[0][w]*d2[0][w]
	return prod/(d1[1]*d2[1])


documents = {}

for i in fo:
	if i != "\n":
		doc_dict = {}
		d = i.translate(string.maketrans("", ""), string.punctuation+'\n')
		d = d.lower()
		d = str.split(d, '\t', 1)
		d[1] = str.split(d[1], ' ')
		l = 0
		for w in d[1]:
			if words[w]>min_idf:
				doc_dict[w] = doc_dict.get(w, 0)+ 1
		for w in doc_dict:
			doc_dict[w] = doc_dict[w]*words[w]
			l += pow(doc_dict[w], 2)
		l = math.sqrt(l)
		documents[d[0]] = (doc_dict, l)


for q in query:
	sims = []
	for w in documents:
		sims.append((sim(documents[q], documents[w]), w))
	sims.sort()
	sims.reverse()
	print(q, sims[0:n_res])





