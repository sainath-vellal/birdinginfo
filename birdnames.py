import glob, os , email, email.iterators, re
import jwzthreading as jwz
import nltk
from nltk.corpus import stopwords


DISTANCE = 2

def build_dic_words():
	fp = open('BigBirdList.csv')
	blist = fp.read()
	fp.close()
	words = [l.strip().lower() for l in blist.splitlines()]
	for j in [w.split() for w in words]:
		if dic.has_key(j[-1]) == True:
			dic[j[-1]].append(j)
		else:
			dic[j[-1]] = [j]


def prune_text(text, sent):
	t = text.splitlines()
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
	prune_text(text, sent)
	ptext = [d for d in sent.itervalues()]
	p = ' '.join(ptext)
	return p
				

def process_single_message(ctr, depth=0,sent={}):
	if(ctr.message == None):
		return
	msg = ctr.message.message 

	print "processing %s"%ctr.message.path
        text = ""
        if(msg.is_multipart()):
                for part in email.iterators.typed_subpart_iterator(msg, 'text','plain') :
                                text = text + part.get_payload(decode=True)

        else :
                text = msg.get_payload(decode=True)
	
	s = extract_original_message(text,sent)
	process_text(s)

	for c in ctr.children:
		process_single_message(c, depth+1, sent)


def search_dict_3(words):
	for x,y,z in words:
		if dic.has_key(z):
			for l in dic[z]:
				if [x,y,z] == l:
					print "Found: %s %s %s" %(x,y,z)
				elif [x,y] == l:
					print "Found: %s %s"%(x,y)
				elif [y,z] == l:
					print "Found: %s %s"%(y,z)
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
	t1 = re.sub(r'[^a-zA-Z]',r' ',t)
	t = t1.split(' ')
	t1 = [w.lower() for w in t if w.lower() not in stopwords.words('english') and w!='']
	return ' '.join([re.sub(r's$',r'',w).lower() for w in t1]) #remove all plurals. This is not right! but will work for now.


def process_text(text=None):
	text = filter_text(text)
	words = nltk.word_tokenize(text)
	tgrams = nltk.trigrams(words)
	search_dict_3(tgrams)
	

birdlist = dict()
dic = dict()
build_dic_words()


files = glob.glob(os.path.join(os.getcwd(),'mails/*.eml'))
msglist = []

for file in files:
	fp = open(file,'r')
	msg = email.message_from_file(fp)
	m = jwz.make_message(msg,file)
	msglist.append(m)
        fp.close()
	

subject_table = jwz.thread(msglist)
L = subject_table.items()
L.sort()
for subj, container in L:
	sent={}
	depth=0
	process_single_message(container,depth,sent)
