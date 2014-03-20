#!/usr/local/bin/python3
true_file = open('lexiconized_brown_test', 'r')
tag_file = open('base_tag_brown_test', 'r')

index = 0
correct = 0
wrong = 0
tags = {}
for segment in true_file:
	index += 1
	tokens = segment.rstrip('\n').split(' ')
	t_tokens = tag_file.readline().strip('\n').split(' ')
	if len(tokens) != len(t_tokens):
		print('error in line')
		print(index)
	for i in range(len(tokens)):
		if tokens[i] != '' and t_tokens != '' and tokens[i] != ' ' and t_tokens != ' ':
			[word, tag] = tokens[i].rsplit('/', 1)
			[word2, tag2] = t_tokens[i].rsplit('/',1)
			if word != word2:
				print('error in line ' + word + ' ' + word2)
				print(index)
			if tag not in tags.keys():
				tags[tag]={'correct':0, 'wrong':0}

			if tag == tag2:
				tags[tag]['correct'] += 1
				correct +=  1
			else:
				tags[tag]['wrong'] += 1
				wrong += 1
				if tag2 not in tags[tag].keys():
					tags[tag][tag2] = 1
				else:
					tags[tag][tag2] += 1

print('correct tags: ', correct)
print('wrong tags: ', wrong)
print('error rate: ', wrong/(correct+wrong))

avg_error_rate = 0
for t in tags:
	avg_error_rate += tags[t]['wrong']/((tags[t]['wrong']) + (tags[t]['correct']))
avg_error_rate = avg_error_rate/len(tags)

print('Average error rate per tag: ', avg_error_rate)

jjs = tags['JJS']
jjs_count = jjs['correct'] + jjs['wrong']
print('JJS accuracy: ', jjs['correct']/jjs_count,' ', jjs_count)
del jjs['correct']
del jjs['wrong']
errors=[]
for t in jjs:
	errors.append((jjs[t], t))
errors.sort()
print('Common JSS errors:')
for e in errors[-2:]:
	print(e[1], ' ', e[0]/jjs_count, ' ', e[0])

jjs = tags['NP']
jjs_count = jjs['correct'] + jjs['wrong']
print('NP accuracy: ', jjs['correct']/jjs_count, ' ', jjs_count)
del jjs['correct']
del jjs['wrong']
errors=[]
for t in jjs:
	errors.append((jjs[t], t))
errors.sort()
print('Common NP errors:')
for e in errors[-2:]:
	print(e[1], ' ', e[0]/jjs_count, ' ', e[0])

true_file.close()
tag_file.close()

 
		

