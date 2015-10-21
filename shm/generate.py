#!/usr/bin/env python

import re
import sys
import commands
from collections import defaultdict

# TODO: brandweerman, dagdagelijks, dakwerker, voetbal => min_length = 3 is gevaarlijk, maar mss beperken tot begin/einde?
# TODO: on-, wan- => ook gevaarlijk
# TODO: lowercase
# TODO: comparatieven bvb groter
# TODO: speciale behandeling van getallen
# TODO: wat met morfemen? bvb aange-, -ingen, -erik, -heid, uitv-, vann-, verw- ? => hopelijk lm kans laag, anders manueel blokkeren als gekende fouten in lex?
# TODO: is er een pos tagger in cornetto? 2e deel moet zelfde zijn als woord, maar bij voorkeur ook gewoon alles SUBST => minder fouten
# TODO: kan EWN nuttig zijn?
# TODO: test vershil in kans

# TOCH WEL NUTTIG OM OOK N-GRAMMEN TE VERGELIJKEN

def info(s):
	if DEBUG:
		sys.stderr.write(str(s) + '\n')

def prefixes():
	prefixes = []
	prefixes.append('on')
	prefixes.append('wan')
	return prefixes

def rules():
	rules = []
	rules.append('s') # Verbruiksatelier, criminaliteitsnieuws, ...
	rules.append('en') # vijfentwintig, ...
	rules.append('-') # 

	return rules
	#return ['jes','je','pjes']

def decompound(w,orig,info_pre='',allow_oov_mod='NONE'):
	r = []
	info(info_pre + 'Decompounding ' + w + ':')
	info_pre_old = info_pre
	info_pre = info_pre + '\t'
	if len(w) < MIN_LENGTH_COMPOUND:
		info(info_pre + w + ' too short to decompound')
	else:
		for i in range(1,len(w)):
			w1 = w[:i]
			w2 = w[i:]
			i1 = inflect(w1, info_pre=info_pre)
	#		if i1 == '':
	#			i1 = decompound(w1)
			if i1 == '' and allow_oov_mod != 'NONE' and len(w1) >= 6 and len(w2) >= 6:
				i1 = w1
			if (i1 != ''):
				if (orig.endswith(w2)):
					i2 = inflect(w2,'>', info_pre)
				else:
					i2 = inflect(w2, info_pre=info_pre)
				if (i2 != ''):
					r.append([i1,i2])
				if allow_oov_mod == 'FULL':
					i2 = decompound(w2,orig,info_pre+'\t',allow_oov_mod)
				else:
					i2 = decompound(w2,orig,info_pre+'\t')
				if (i2 != []):
					r.append([i1,i2])
	if r != []:
		info(info_pre_old + 'Decompounding ' + w + ' succesful')
	else:
		info(info_pre_old + 'Decompounding ' + w + ' unsuccesful')
	return r

def isupper(w):
	return w.isupper() and "'" not in w

def inflect(word,pos='<',info_pre=''):
#	if word in prefixes() and pos != '>':
#		return word + ' (PREFIX) '
	w = ''
	code = ''
	if pos == '<':
		if len(word)>=2 and (isupper(word) or (isupper(word[0:-1]) and word[-1] == '-')):
			w = word.replace('-','')
			code = 'ACRO'
		elif len(word) < MIN_LENGTH_MODIFIER:
			return ''
	elif len(word) < MIN_LENGTH_HEAD:
		return ''
	if pos == '<':
		lex = mods_lex
	else:
		lex = heads_lex
	if word in lex:
		info(info_pre + word + ' in lexicon')
		w = word
		code = 'LEX'
#		return word + ' (LEX)'
	elif (pos != '>'):
		for r in rules():
			if (word.endswith(r)) and word[:-len(r)] in lex:
				w = word[:-len(r)]
				code = 'INFL:' + r
#				return word[:-len(r)] + ' (INFL:' + r + ')'
	if w != '':
		#return '%s (%s) [%.1f]' % (w,code,puni.get(w,-99))
		return '%s (%s)' % (w,code)
	return ''

def flatten2(tree):
#	info(tree)
	s = ''
	leaf = True
	for el in tree:
		if not isinstance(el,str):
			leaf = False
			break
	if not leaf:
		if isinstance(tree[0],str):
			l = len(tree[1])
			for i in range(0,l):
				s += '{0:^25} + '.format(tree[0])
				s += flatten2(tree[1][i])
	else:
		l = len(tree)
		for i in range(0,l):
			s += '{0:^25}'.format(tree[i])
			if i != l-1:
				s += ' + '
	return s

def flatten3(tree):
	info(tree)
	r = []
	for b in tree:
		leaf = True
		for el in b:
			if not isinstance(el,str):
				leaf = False
				break
		# b = [A,[B,C]]
		if not leaf:
			if isinstance(b[0],str):
				l = len(b[1])
				for i in range(0,l):
					s = '{0:^25} + '.format(b[0])
					s += flatten2(b[1][i])
					r.append(s)
		# b = [A,B]
		else:
			r.append(flatten2(b))
	return r

# I don't think this criterion makes sense, since after mapping the count of the head is always larger

#class CountCrit:
#	def __init__(self, f):
#		self.puni = {}
#		if counts.endswith(".cnt"):
#			sys.stderr.write("Reading counts... ")
#			foundHeader = True
#		else:
#			sys.stderr.write("Reading puni's... ")
#			foundHeader = False
#		for line in open(f,'r'):
#			if foundHeader:
#				l = line.strip().split()
#				self.puni[l[0]] = float(l[1])
#			elif (line.startswith('#')):
#				foundHeader = True
#		sys.stderr.write("%i entries\n" % len(puni))
#
#	def complies(self, word, head):
#		return self.puni.get(word,-99) < self.puni[head]

def parseArguments(args):
	if len(args) < 2:
		sys.stderr.write('Usage: decompounding.py <wlist> [<option>*]\n\n')
		sys.stderr.write('Performs a decompounding analysis: lists all possible decompoundings for the given word list according to some options\n')
		sys.stderr.write('List of possible options:\n')
		sys.stderr.write('\t* {0:30}\tUse the given word list as decomposition lexicon instead of the original word list\n'.format("parts=<parts-wlist>"))
		sys.stderr.write('\t* {0:30}\tUse the given word list as decomposition lexicon for the modifiers only instead of the original word list\n'.format("mods=<mods-wlist>"))
		sys.stderr.write('\t* {0:30}\tUse the given word list as decomposition lexicon for the heads only instead of the original word list\n'.format("heads=<heads-wlist>"))
		sys.stderr.write('\t* {0:30}\tAllow (each|only the main|no) modifier to be oov as long as it is  at least 6 characters long\n'.format("allow_oov_mod=FULL|HALF|NONE"))
		sys.stderr.write("\t* {0:30}\tSet the minimum length for the compound to the given value\n".format("min_length_compound=<value>"))
		sys.stderr.write("\t* {0:30}\tSet the minimum length for the modifiers to the given value\n".format("min_length_mod=<value>"))
		sys.stderr.write("\t* {0:30}\tSet the minimum length for the head to the given value\n".format("min_length_head=<value>"))
		sys.stderr.write("\t* {0:30}\tUse the given decompounding database (overrides any automatic decompounding for the contained words)\n".format("dbase=<dbase>"))
		sys.stderr.write("\t* {0:30}\tEnable debugging\n".format("debug=TRUE"))
		sys.exit(1)
	else:
		wlist = args[1]
		mods_lex = wlist
		heads_lex = wlist
		min_length_compound = 4
		min_length_modifier = 4
		min_length_head = 3
		allow_oov_mod = 'NONE'
		dbase = ''
		debug = False
		criteria = []
		for i in range(2,len(args)):
			o = args[i].split('=')
			if o[0] == 'parts':
				mods_lex = o[1]
				heads_lex = o[1]
			elif o[0] == 'mods':
				mods_lex = o[1]
			elif o[0] == 'heads':
				heads_lex = o[1]
#			elif o[0] == 'counts':
#				criteria.append(CountCrit(o[1]))
			elif o[0] == 'allow_oov_mod':
				aom = o[1]
				if aom != 'NONE' and aom != 'FULL':
					aom = 'HALF'
				sys.stderr.write('Setting allow_oov_mod to {0}\n'.format(aom))
				allow_oov_mod = o[1]
			elif o[0] == 'min_length_compound':
				sys.stderr.write('Setting min_length_compound to {0}\n'.format(o[1]))
				min_length_compound = int(o[1])
			elif o[0] == 'min_length_mod':
				sys.stderr.write('Setting min_length_mod to {0}\n'.format(o[1]))
				min_length_modifier = int(o[1])
			elif o[0] == 'min_length_head':
				sys.stderr.write('Setting min_length_head to {0}\n'.format(o[1]))
				min_length_head = int(o[1])
			elif o[0] == 'dbase':
				sys.stderr.write('Reading decompounding database {0}\n'.format(o[1]))
				dbase = o[1]
			elif o[0] == 'debug':
				sys.stderr.write('Enabling debug mode\n')
				debug = True
			else:
				sys.stderr.write('ERROR: Unknown option: {0}\n'.format(o[0]))
				sys.exit(1)
		return wlist, heads_lex, mods_lex, criteria, min_length_compound, min_length_modifier, min_length_head, allow_oov_mod, dbase, debug



if __name__ == '__main__':
	f_wlist, f_heads_lex, f_mods_lex, criteria, MIN_LENGTH_COMPOUND, MIN_LENGTH_MODIFIER, MIN_LENGTH_HEAD, allow_oov_mod, dbase, DEBUG = parseArguments(sys.argv)

	if f_mods_lex == f_heads_lex:
		sys.stderr.write("Reading lexicon {0}... ".format(f_heads_lex))
	else:
		sys.stderr.write("Reading heads lexicon {0}... ".format(f_heads_lex))
#	heads_lex= []
	heads_lex = {}
	for line in open(f_heads_lex,'r'):
#		heads_lex.append(line.strip())
		heads_lex[line.strip()] = ''
	sys.stderr.write("%i entries\n" % len(heads_lex))
	
	if f_mods_lex == f_heads_lex:
		mods_lex = heads_lex
	else:
		sys.stderr.write("Reading mods lexicon {0}... ".format(f_mods_lex))
#		mods_lex= []
		mods_lex = {}
		for line in open(f_mods_lex,'r'):
#			mods_lex.append(line.strip())
			mods_lex[line.strip()] = ''
		sys.stderr.write("%i entries\n" % len(mods_lex))

	sys.stderr.write("Reading decompounding database {0}... ".format(dbase))
	db = defaultdict(list)
	if dbase != '':
		for line in open(dbase,'r'):
			l = line.strip().split()
			if len(l) == 2:
				orig = ''.join(l)
				if len(l[0]) >= MIN_LENGTH_MODIFIER and len(l[1]) >= MIN_LENGTH_HEAD and len(orig) >= MIN_LENGTH_COMPOUND:
				#if True:
					if l[0].endswith('-'):
						l[0] = l[0][:-1]
					db[orig].append(l)
			else:
				db[l[0]] = []

	sys.stderr.write("Reading word list {0}...\n".format(f_wlist))
	wlist = open(f_wlist,'r')
	count = 0
	no_decomp = 0
	total = int(commands.getoutput('wc -l ' + f_wlist).split()[0])
	for line in wlist:
		w = line.strip()
		info('=========')
		hypos = []
		if w in db:
			if len(db[w]) != 0:
				for val in db[w]:
					h = ' + '.join(val)
					hypos.append(h)
#					sys.stdout.write('{0:>30} = {1}\n'.format('* ' + w, h))
#			else:
#				sys.stdout.write('{0:>30} = ?\n'.format(w))
#				no_decomp += 1
		else:
			d = decompound(w,w,allow_oov_mod=allow_oov_mod)
			if d == []:
				#sys.stdout.write('{0:>30} [{1:^5.1f}] = ?\n'.format(w,puni.get(w,-99)))
				sys.stdout.write('{0:>30} = ?\n'.format(w))
				no_decomp += 1
			else:
		#		sys.stdout.write('%s\n' % d)
				hypos = flatten3(d)
		for h in hypos:
			complies = True
			for c in criteria:
				complies = complies and c.complies(w,h)
			if complies:
				pre = '* '
#				sys.stdout.write('{0:>30} [{1:^5.1f}] = {2}\n'.format(pre + w,puni.get(w,-99), hypos[i]))
			sys.stdout.write('{0:>30} = {1}\n'.format(pre + w, h))

	# THE BELOW BELONGS IN A COMPARISON MODULE

	#		sums = []
	#		for h in hypos:
	#			s = 0
	#			p = puni.get(h.split('+')[-1].split()[0],-99)
	#			if pw < p:
	#				for part in h.split('+'):
	#					s += puni.get(part.split()[0],-99)
	#					#s += puni[part.split()[0]]
	#				sums.append(s)
	#			else:
	#				sums.append(-99)
	#		# find max in sums
	#		m = max(sums)
	#		indices = [i for i,j in enumerate(sums) if j == m and m != -99]
	#		for i in range(0,len(hypos)):
	#			pre = ''
	#			if i in indices:
	#				pre = '* '
	#			if pw == -99:
	#				pre = '[OOV] ' + pre
	#				pre = '[OOV] ' 
	#			sys.stdout.write('{0:>30} [{1:^5.1f}] = {2}\n'.format(pre + w,puni.get(w,-99), hypos[i]))
		count += 1
		sys.stderr.write('%i/%i words processed\n' % (count,total))
	sys.stderr.write('{0} possible compound(s) found\n'.format(total - no_decomp))
