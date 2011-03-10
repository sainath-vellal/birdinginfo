import re,pdb,codecs
import pymongo
from pymongo import Connection

dic = {}	 
def parse():
	text = codecs.open('SouthAsianOrnithology.txt').read()
	para  = text.split('ER  -')
	records = [w.split('\n') for w in para if w!='']
	
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
			v = lst['ID'].strip()
			dic[v] = lst
	
	i = 0
	vals = [[] for i in range(10)]
	for v in dic.values():
		vals[i%10].append(v)
		i += 1


	conn = Connection()
	db = conn['test']
	for i in range(10):
		db['coll_%s'%i].insert(vals[i])

if __name__ == "__main__":
	parse()
