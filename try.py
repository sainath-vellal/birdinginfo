import glob, os , email, email.iterators, re
import jwzthreading as jwz
import nltk
from nltk.corpus import stopwords
from collections import defaultdict

import pdb

DISTANCE = 2

cdic = defaultdict(lambda: 0)

def build_dic_words():
	fp = open('BigBirdList.csv')
	blist = fp.read()
	fp.close()
	words = [l.strip().lower() for l in blist.splitlines()]
	#uniq_last_words = [l for l in set([j[-1] for j in [w.split() for w in words] ])]
	for j in [w.split() for w in words]:
		for i in j:
			cdic[i]=1

		if dic.has_key(j[-1]) == True:
			dic[j[-1]].append(j)
		else:
			dic[j[-1]] = [j,[j[-1]]]


def prune_text(text, sent):
	t = text.splitlines()
	#put the split lines into a dictionary with its hash.
	for a in t:
		if a == '':
			continue
		if a.startswith('>'):
			#print "Reply text found! ignoring %s"%a
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
	#pdb.set_trace()
	text = """ My first posting to this group. Apologies if this is too mundane.
	 
	 We and the family had gone to Melukote yesterday and we spotted quite a few birds yesterday on Mandya to Melukote road. Particularly happy about the Hornbills.... and about the White throated Kingfisher photo attached!
	  
	  Bird list 
	  1. Malabar Grey hornbill
	  2. Indian Grey hornbill (spotted in 2 different locations)
	  3. Indian roller (quite a few)
	  4. White throated Kingfisher (many many..)
	  5. purple rumped sunbird
	  6. Red Junglefowl
	  7. Hoopoe
	  8. Green Bee-eater
	  9. Blue tailed Bee-eater
	  10.Greater Coucal
	  11. Vernal Hanging Parrot
	  12. Rose Ringed Parakeet
	  13. Black bellied Tern
	  14. Black ibis
	  15. Egret (Greater and Little)
	  16. Common coot
	  17. Common moorhen
	  18. Red wattled Lapwing
	  19. Pond herons
	  20. Cormorants  
	  """
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
	process_text(jw)

	#pdb.set_trace()
	for c in ctr.children:
		#pdb.set_trace()
		process_single_message(c, depth+1, sent)


def search_dict_3(words):
	pdb.set_trace()
	skip_cnt = 0
	for x,y,z in words:
		if skip_cnt > 0:
			skip_cnt-=1
			continue
		if dic.has_key(z):
			for l in dic[z]:
				if [x,y,z] == l:
					print "Found: %s %s %s" %(x,y,z)
					#skip_cnt=2
				elif [x,y] == l:
					print "Found: %s %s"%(x,y)
					#skip_cnt=1
				elif [y,z] == l:
					print "Found: %s %s"%(y,z)
					#skip_cnt=1
				elif [z] == l:
					print "Found: %s"%(z)
				else:
					if nltk.metrics.distance.edit_distance(' '.join([x,y,z]),' '.join(l)) <= DISTANCE:
						print "Probable bird name Found!! %s %s %s -> %s "%(x,y,z,l)
					elif nltk.metrics.distance.edit_distance(' '.join([x,y]),' '.join(l)) <= DISTANCE:
						print "Probable bird name Found!! %s %s -> %s "%(x,y,l)
					elif nltk.metrics.distance.edit_distance(' '.join([y,z]),' '.join(l)) <= DISTANCE:
						print "Probable bird name Found!! %s %s -> %s "%(y,z,l)


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
	text = filter_text(text)
	words = nltk.word_tokenize(text)
	pdb.set_trace()
	tgrams = [w for w in nltk.trigrams(words)]
	search_dict_3(tgrams)
	
	#search_dict_new_3(tgrams)
	#search_dict_2(bgrams)
	
#fi = os.path.join(os.getcwd(),"test file .gg")

birdlist = dict()
dic = dict()
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
"""
t = threadMessages.jwzThread(msglist)
printSubjects(t)
"""
