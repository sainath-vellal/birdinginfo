import re,pdb,codecs
import simplejson
import pymongo
from pymongo import Connection
from pymongo import son

dic = {}	 
ll = []
def parse():
	text = codecs.open('SouthAsianOrnithology.txt').read()
	para  = text.split('ER  -')
	records = [w.split('\r\n') for w in para if w!='']
	
	for i,rec in enumerate(records):
		lst = {}
		for line in rec:
			if line.strip() == '':
				continue
			l = line.partition('-')
			k = l[0].lstrip(codecs.BOM_UTF8).strip()
			if (l[1] == '-') and (len(k)==2):
				val = l[2].strip()
				if k == 'KW':
					val = [v.strip() for v in l[2].split(';')]
				if lst.has_key(k):
					lst[k].append(val)
				else:
					if k == 'KW':
						lst[k] = val
					else:
						lst[k] = [val]
				lkey = k
			else:
				try:
					lst[k].append(line.strip())
				except:
					try:
						lst[lkey].append(line.strip())
					except:
						pdb.set_trace()
		
		if lst == {}:
			continue
		else:
			for ke,va in lst.items():
				if len(va) == 1:
					lst[ke] = va[0]
				else:
					try:
						lst[ke] = '::'.join(va)
					except:
						pdb.set_trace()
			v = lst['ID'].strip()
			dic[v] = lst
	
	i = 0
	keys = [[] for i in range(10)]
	dics = [{} for i in range(10)]
	vals = [[] for i in range(10)]
	for k,v in dic.items():
		keys[i%10].append(k)
		vals[i%10].append(v)
		i += 1
	for i in range(10):
		dics[i] = dict(zip(keys[i],vals[i]))


	conn = Connection()
	db = conn['test']
	for i in range(10):
		db['coll_%s'%i].insert(vals[i])
	pdb.set_trace()

if __name__ == "__main__":
	parse()
