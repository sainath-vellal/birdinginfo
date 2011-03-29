import glob, os , email, email.iterators, re
import jwzthreading as jwz
import nltk
from nltk.corpus import stopwords
from collections import defaultdict

import pdb


sentences = []
dic = defaultdict(lambda:{}) 

seen_word_variations = []
list_of_birds = set() 
report_words = []
word_to_sent = defaultdict(lambda: [])
reg_remove_special_chars = re.compile(r'[^a-zA-Z]')

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
	word_to_sent.clear()
	report_words[:] = []
	seen_word_variations[:] = []


def convert_lower(text):
	ws = nltk.wordpunct_tokenize(text)
	return  ' '.join([''.join(s.lower()) for s in ws ])
	
def plural(word):
    if word.endswith('y'):
        return word[:-1] + 'ies'
    elif word[-1] in 'sx' or word[-2:] in ['sh', 'ch']:
        return word + 'es'
    elif word.endswith('an'):
        return word[:-2] + 'en'
    return word + 's'


def build_dic_words():
	fp = open('BigBirdList.csv')
	blist = fp.read()
	fp.close()
	words = [l.strip().lower() for l in blist.splitlines()]
	words1 = []
	for j in [w.split() for w in words]:
		words1.append(j[0:-1]+[plural(j[-1])])
		words1.append(j)
		list_of_birds.add(j[-1])

	for j in words1:
		for k in j:
			bird = k
			for i in range(len(j)):
				hsh = ''.join(sorted(''.join(j[i:])))
				dic[bird][hsh] = ' '.join(j[i:])
				if dic[bird].has_key('len'):
					if (dic[bird]['len'] < len(j)-1):
						dic[bird]['len'] = len(j)-1
				else:
					dic[bird]['len'] = len(j)-1



def build_word_to_sent_map(text = None):
	text1 = ' '.join([i.lower() for i in text.split(' ')])	
	tex = nltk.sent_tokenize(text1)
	for sent_num,te in enumerate(tex):
		t = te.splitlines()	
		for sp_num,j in enumerate(t):
			j1 = reg_remove_special_chars.sub(r' ',j)
			j2 = nltk.wordpunct_tokenize(j1)
			for index,k in enumerate(j2):
				if len(k)>2 and k not in stopwords.words('english'):
					word_to_sent[k].append((sent_num,sp_num, index))

	return tex

def prune_text(text, sent):
	global sentences 
	sentences = build_word_to_sent_map(text)
	tex = []
	tex.extend(sentences)
	for i,t in enumerate(tex):

		t1 = t.splitlines()
		for a in t1:
			if a == '' or  a.startswith('>'):
				continue
			p_text = ''.join(sorted(re.sub(r'[^a-zA-Z]',r'',a).lower()))
			if p_text == '':
				continue
			sent[a] = 1


def extract_original_message(text,sent):
	prune_text(text, sent)
	joined_words = ' '.join(sent.keys())
	return (joined_words)
				

count = 0
reg_replace_slashn = re.compile(r'\n')
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
	
	
	"""text = 
	Bird List of Lalbagh(Pictures here:
	http://bangalorecaptured.com/2011/03/14/birds-and-flowers-again-lalbagh/) :

	Barbet, white cheeked
	Cormorant, Great
	Cormorant, Little
	Crow, Jungle
	Crow, House
	Dove, Spotted
	Drongo, Ashy
	Drongo, Black
	Duck, Spot Biled
	Egret, Little
	Egret, Cattle*
	*Flowerpecker, pale billed*
	Goose, Bar Headed*
	Heron, Pond
	Heron, Grey
	Kingfisher, White throated
	Kite, Black
	Kite, Brahminy
	Koel, Asian (male and female)
	Moorhen, Purple
	Mynah, Commmon
	Mynah, Jungle
	Oriole, Golden
	Owlet, Spotted
	Parakeet, Rose Ringe*d
	*Sunbird, Purple Rumped
	Tailorbird, Common

	Thanks,
	Vaibhav
	"""

	jw = extract_original_message(text,sent)
	process_text(jw)
	reset_data()
	for c in ctr.children:
		process_single_message(c, depth+1, sent)


def get_word_instances(w,maxw):
	l = word_to_sent[w]
	ll = []
	for (x,y,z) in l:
		split = sentences[x].splitlines()
		sen = split[y]	
		j1 = reg_remove_special_chars.sub(r' ',sen)
		j2 = nltk.wordpunct_tokenize(j1)
		jj = j2[lb(z-maxw):z+1]
		kk = j2[z:z+maxw+1]

		jj1 = [jj[i:] for i in range(len(jj))]
		jj2 = [kk[:i+1] for i in range(len(kk))]
		for k in jj1:
			if k not in ll:
				ll.append((k,(x,y,z-(len(k)-1),z,0)))
		for k in jj2:
			if k not in ll:
				ll.append((k,(x,y,z,z+len(k)-1,1)))
		
	return ll

def hash_val(x):
	return ''.join(sorted(''.join(x)))

def cmp_by_len(w1,w2):
	return len(w2[0])-len(w1[0])

def search_dict(words):
	#locations = set() 
	words = set(words)
	locations = [] 
	for x in words:
		if x in dic:

			lw = get_word_instances(x,dic[x]['len'])
			#for lo in loc:
			#	locations.add(lo)
			#	locations.append(lo)
			lw.sort(cmp=cmp_by_len)
			for w in lw:
				hsh = hash_val(w[0])
				for key in dic[x].keys():
					dist = nltk.metrics.edit_distance(hsh,key)
					if dist < 2  and w[0] not in report_words and hsh not in seen_word_variations:
						"""
						valid = False
						for h in w[0]:
							if h in list_of_birds:
								valid = True
						if valid == False:
							continue
						"""
						report_words.append(w[0])
						(a,b,c,d,e) = w[1]
						locations.append((a,b,c,d))
						for i in range(len(w[0])):
							if e == 0:
								seen_word_variations.append(hash_val(w[0][i:]))
							else:
								seen_word_variations.append(hash_val(w[0][:i]))
	return locations

		
def filter_text(text):
	t = nltk.wordpunct_tokenize(text)
	t1 = [w.lower() for w in t if w.lower() not in stopwords.words('english') and w!='' and w.lower() in list_of_birds]
	return ' '.join(t1)


def write_to_orig_html_file(sentences):
	global count
	t = '\n'.join(sentences)
	f = open('html/%d_orig.html'%count, "w")
	t = reg_replace_slashn.sub(r'<br/>',t)
	f.write(t)
	f.close()


def group_locs_by_sentences(locs):
	g_dic = defaultdict(lambda:[])
	for (x,y,a,b) in locs:
		g_dic[(x,y)].append((a,b))
	return g_dic

def cmp_by_ind(a,b):
	return a[0]-b[0]

def write_to_mod_html_file(sentences,locs,tex):
	global count
	g_dic = group_locs_by_sentences(locs)
	ll= []
	for l in g_dic.keys():
		ll.append(l)
	ll.sort(cmp=cmp_by_ind)
	for (x,y) in ll:
		l = g_dic[(x,y)]
		sen = sentences[x]
		slash_n_split = sen.splitlines()
		wds = reg_remove_special_chars.sub(r' ',slash_n_split[y])
		words = nltk.wordpunct_tokenize(wds)
		l.sort(cmp=cmp_by_ind)
		for (h,k) in l:
			words[h] = """<i style="color:red">"""+words[h]
			words[k] = words[k]+'</i>'
		
		words = ' '.join(words)
		slash_n_split[y] = words
		sentences[x] = '\n'.join(slash_n_split)
	t = '\n'.join(sentences)

	f = open('html/%d_mod.html'%count, "w")
	t = reg_replace_slashn.sub(r'<br/>',t)
	f.write(t)
	f.close()
	count +=1

def process_text(text=None):
	tex = filter_text(text)
	print sorted(set(tex.split(' '))),len(set(tex.split(' ')))
	write_to_orig_html_file(sentences)
	words = nltk.wordpunct_tokenize(tex)
	locs = search_dict(words)
	write_to_mod_html_file(sentences,locs,tex)
	print sorted(report_words), len(report_words)
	

build_dic_words()


files = glob.glob('/root/bngbirds-data/bngbirds/*.eml')
msglist = []

for file in files[:10]:
	fp = open(file,'r')
	msg = email.message_from_file(fp)
	m = jwz.make_message(msg,file)
	msglist.append(m)
        fp.close()
	

subject_table = jwz.thread(msglist)
L = subject_table.items()
L.sort()
for subj, container in L:
	sent=defaultdict(lambda: 0)
	depth=0
	process_single_message(container,depth,sent)
