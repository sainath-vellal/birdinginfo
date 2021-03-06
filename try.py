import glob, os , email, email.iterators, re
import jwzthreading as jwz
import nltk
from nltk.corpus import stopwords
from collections import defaultdict
import json

import pdb

DISTANCE = 3 

gen_dict = defaultdict(lambda: 0)
gen_dict_p = defaultdict(lambda: 0)
sp_dict = defaultdict(lambda: 0)
sp_dict_p = defaultdict(lambda: 0)
prob_dict = defaultdict(lambda:0)
dic_p = {}
p_to_s = {}
sentences = []
dic = defaultdict(lambda:{}) 

report_words = []
word_to_sent = defaultdict(lambda: [])
reg_remove_special_chars = re.compile(r'[^a-zA-Z]')
reg_remove_special_chars_without_nl = re.compile(r'[^a-zA-Z\n,]')

def lb(x):
	if x<0:
		return 0
	else:
		return x

def ub(x,l):
	if x>l:
	 	return l
	else:
		return x

def reset_data():

	gen_dict.clear() 
	gen_dict_p.clear()
	sp_dict.clear()
	sp_dict_p.clear()
	prob_dict.clear()


def convert_lower(text):
	ws = nltk.word_tokenize(text)
	return  ' '.join([''.join(s.lower()) for s in ws ])
	
def plural(word):
    if word.endswith('y'):
        return word[:-1] + 'ies'
    elif word[-1] in 'sx' or word[-2:] in ['sh', 'ch']:
        return word + 'es'
    elif word.endswith('an'):
        return word[:-2] + 'en'
    return word + 's'

def generate_report():
	gen_birds = gen_dict.keys()
	gb=[]
	for i in gen_birds:
		if p_to_s.has_key(i):
			gb.append(p_to_s[i])
		else:
			gb.append(i)

	sp_birds = [x[-1] for x in sp_dict.keys()]

	gen_birds = [i for i in set(gb) - set(gb).intersection(set(sp_birds))]
	
	print "--------------Specific birds-------------\n"
	for i in sp_dict.keys():
		print i
	print "-------------Generic birds--------------\n"
	for i in gen_birds:
		print i
	print "------------Probable bird sightings-------\n"
	for x,y in prob_dict.items():
		print x,"-->",y 

def build_dic_words():
	fp = open('BigBirdList.csv')
	blist = fp.read()
	fp.close()
	words = [l.strip().lower() for l in blist.splitlines()]
	for j in [w.split() for w in words]:
		for i in range(len(j)):
			hsh = ''.join(sorted(''.join(j[i:])))
			dic[j[-1]][hsh] = ' '.join(j[i:])
			if dic[j[-1]].has_key('len'):
				if (dic[j[-1]]['len'] < len(j)-1):
					dic[j[-1]]['len'] = len(j)-1
			else:
				dic[j[-1]]['len'] = len(j)-1
		
		p = plural(j[-1])
		k = []
		k.extend(j) #right way to copy a list :-) 	
		if dic_p.has_key(p):
			k[-1]= p
			dic_p[p].append(k)
		else:
			k[-1] = p
			dic_p[p] = [k,[p]]
			p_to_s[p] = j[-1]



def build_word_to_sent_map(text = None):
	text1 = ' '.join([i.lower() for i in text.split(' ')])	
	tex = nltk.sent_tokenize(text1)
	for sent_num,te in enumerate(tex):
		t = te.splitlines()	
		for sp_num,j in enumerate(t):
			j1 = reg_remove_special_chars.sub(r' ',j)
			j2 = nltk.word_tokenize(j1)
			for index,k in enumerate(j2):
				if len(k)>2 and k not in stopwords.words('english'):
					word_to_sent[k].append((sent_num,sp_num, index))

	tex1 = []
	for te in tex:
		tex1.append(reg_remove_special_chars_without_nl.sub(r' ',te))
	return tex1

def prune_text(text, sent):
	pdb.set_trace()
	global sentences 
	sentences = build_word_to_sent_map(text)
	tex = nltk.sent_tokenize(text)
	#tex1 = re.sub(r'[^a-zA-Z]',r' ',text).lower()
	#w = nltk.word_tokenize(tex1)
	for i,t in enumerate(tex):

		t = text.splitlines()
		#put the split lines into a dictionary with its hash.
		for a in t:
			if a == '' or  a.startswith('>'):
				continue
			p_text = ''.join(sorted(re.sub(r'[^a-zA-Z]',r'',a).lower()))
			if p_text == '':
				continue
			if sent.has_key(p_text):
				#print "Duplicate text found!!! %s ignoring %s"% (sent[p_text],a)
				continue
			else:
				sent[p_text] = a


def extract_original_message(text,sent):
	#we have the entire text and unique sentence hash from the parent thread.
	#lets hash the text and build a diff of sent and text
	prune_text(text, sent)
	split_words = [d for d in sent.itervalues()]
	joined_words = ' '.join(split_words)
	return (joined_words, split_words)
				

def process_single_message(ctr, depth=0,sent={}):
	if(ctr.message == None):
		return
	msg = ctr.message.message 

	print "processing %s"%ctr.message.path
	#pdb.set_trace()
        text = ""
        if(msg.is_multipart()):
                for part in email.iterators.typed_subpart_iterator(msg, 'text','plain') :
                                text = text + part.get_payload(decode=True)

        else :
                text = msg.get_payload(decode=True)
	
	(jw,w) = extract_original_message(text,sent)
	#pdb.set_trace()
	process_text(jw)
	generate_report()
	reset_data()
	#pdb.set_trace()
	for c in ctr.children:
		#pdb.set_trace()
		process_single_message(c, depth+1, sent)

def lconcord(text=None):
	pass	

def search_word_instances(w,maxw):
	l = word_to_sent[w]
	ll = []
	for (x,y,z) in l:
		split = sentences[x].splitlines()
		try:
			sen = split[y]	
		except:
			pdb.set_trace()
		j1 = reg_remove_special_chars.sub(r' ',sen)
		j2 = nltk.word_tokenize(j1)
		jj = j2[lb(z-maxw):z+1]
		jj1 = [jj[i:] for i in range(len(jj)-1)]
		for k in jj1:
			if k not in ll:
				ll.append(k)
	return ll

def hash_val(x):
	return ''.join(sorted(''.join(x)))

def search_dict(words):
	for x in words:
		if x in dic:
			lw = search_word_instances(x,dic[x]['len'])
			for w in lw:
				hsh = hash_val(w)
				if hsh in dic[x]:
					if w not in report_words:
						report_words.append(w)
				
	#look into plurals later			
#XXX: make it 4grams
def search_dict_3(words):
	#pdb.set_trace()
	for x,y,z in words:
		if dic.has_key(z):
			for l in dic[z]:
				if [x,y,z] == l:
					#print "Found: %s %s %s" %(x,y,z)
					sp_dict[(x,y,z)] += 1
				elif [x,y] == l:
					#print "Found: %s %s"%(x,y)
					sp_dict[(x,y)] +=1
					#skip_cnt=1
				elif [y,z] == l:
					#print "Found: %s %s"%(y,z)
					sp_dict[(y,z)] +=1
					#skip_cnt=1
				elif [z] == l:
					#print "Found: %s"%(z)
					gen_dict[z] += 1
				else:
					if nltk.metrics.distance.edit_distance(' '.join([x,y,z]),' '.join(l)) <= DISTANCE:
						#print "Probable bird name Found!! %s %s %s -> %s "%(x,y,z,l)
						prob_dict[(x,y,z)] = (l,1)
					elif nltk.metrics.distance.edit_distance(' '.join([x,y]),' '.join(l)) <= DISTANCE:
						#print "Probable bird name Found!! %s %s -> %s "%(x,y,l)
						prob_dict[(x,y)] = (l,1)
					elif nltk.metrics.distance.edit_distance(' '.join([y,z]),' '.join(l)) <= DISTANCE:
						#print "Probable bird name Found!! %s %s -> %s "%(y,z,l)
						prob_dict[(y,z)] = (l,1)
						
		elif dic_p.has_key(z):
			for l in dic_p[z]:
				if [x,y,z] == l:
					#print "Found: %s %s %s" %(x,y,z)
					sp_dict[(x,y,z)] += 1
				elif [x,y] == l:
					#print "Found: %s %s"%(x,y)
					sp_dict[(x,y)] +=1
					#skip_cnt=1
				elif [y,z] == l:
					#print "Found: %s %s"%(y,z)
					sp_dict[(y,z)] +=1
					#skip_cnt=1
				elif [z] == l:
					#print "Found: %s"%(z)
					gen_dict[z] += 1
				else:
					if nltk.metrics.distance.edit_distance(' '.join([x,y,z]),' '.join(l)) <= DISTANCE:
						#print "Probable bird name Found!! %s %s %s -> %s "%(x,y,z,l)
						prob_dict[(x,y,z)] = (l,1)
					elif nltk.metrics.distance.edit_distance(' '.join([x,y]),' '.join(l)) <= DISTANCE:
						#print "Probable bird name Found!! %s %s -> %s "%(x,y,l)
						prob_dict[(x,y)] = (l,1)
					elif nltk.metrics.distance.edit_distance(' '.join([y,z]),' '.join(l)) <= DISTANCE:
						#print "Probable bird name Found!! %s %s -> %s "%(y,z,l)
						prob_dict[(y,z)] = (l,1)
			
def filter_text(text):
	t = re.sub(r'\r\n',r' ',text)
	t = re.sub(r'\n',r' ',t)
	#return  re.sub(r'[^a-zA-Z.?]',r' ',t)
	t1 = re.sub(r'[^a-zA-Z]',r' ',t)
	t = t1.split(' ')
	t1 = [w.lower() for w in t if w.lower() not in stopwords.words('english') and w!='']
	#return ' '.join([re.sub(r's$',r'',w).lower() for w in t1]) #remove all plurals. This is not right! but will work for now.
	#pdb.set_trace()
	return ' '.join(t1)


def process_text(text=None):
	#pdb.set_trace()
	tex = filter_text(text)
	words = nltk.word_tokenize(tex)
	#tgrams = [w for w in nltk.ngrams(words,3)]
	
	search_dict(words)
	print report_words
	#search_dict_3(tgrams)
	
	#search_dict_new_3(tgrams)
	#search_dict_2(bgrams)
	
#fi = os.path.join(os.getcwd(),"test file .gg")

build_dic_words()


files = glob.glob('/root/bngbirds-data/bngbirds/*.eml')
#files = glob.glob('/home/sainath/try_email/*.eml')
msglist = []

for file in files[:10]:
#        print '\n'
	fp = open(file,'r')
	msg = email.message_from_file(fp)
	m = jwz.make_message(msg,file)
	msglist.append(m)
#	pdb.set_trace()
        fp.close()
	
       # print "parsing file %s %d "%(file, files.index(file))
"""
"""	
#	print text.lower()
#	print hh

subject_table = jwz.thread(msglist)
L = subject_table.items()
L.sort()
for subj, container in L:
#	jwz.print_container(container)
	sent={}
	depth=0
	process_single_message(container,depth,sent)
