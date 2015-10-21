#! /usr/bin/env python

import sys
import tools
from collections import defaultdict

def parseCrit(crit):
	c = crit.split('=')
	if c[0] == 'max_sum':
		options = c[1].split(':')
		return MaxSumCrit(options[0],float(options[1]))
	elif c[0] == 'max_head':
		options = c[1].split(':')
		return MaxHeadCrit(options[0],float(options[1]))
	elif c[0] == 'like':
		return LikeCrit(float(c[1]))
	elif c[0] == 'pos':
		options = c[1].split(':')
		allow_unknown = 'FALSE'
		if len(options) == 3:
			allow_unknown = options[2]
		return PosCrit(options[0],float(options[1]), allow_unknown)
	elif c[0] == 'rules':
		options = c[1].split(':')
		rules = []
		if ',' in options[1]:
			for r in options[1].split(','):
				rules.append(int(r))
		elif '-' in options[1]:
			interval = options[1].split('-')
			for r in range(int(interval[0]),int(interval[1]) + 1):
				rules.append(r)
		else:
			rules.append(int(options[1]))
		return RulesCrit(options[0],rules,float(options[2]))
	else:
		sys.stderr.write("ERROR: Unknown criterion: {0}\n".format(c[0]))
		sys.exit(1)

class RulesCrit:
	def __init__(self,f_pos,rules,weight,allow_unknown=False):
		# TODO: check empty rules
		sys.stderr.write("Initializing rules criterion with rules={0}... ".format(str(rules)))
		self.rules = rules
		self.weight = weight
#		self.pos = {}
		self.pos = defaultdict(list)
		self.allow_unknown = allow_unknown
		for line in open(f_pos,'r'):
			if line.strip().startswith('<s>') or line.strip().startswith('</s>'):
				continue
			# check for counts
			# TODO: use instead of remove
			l = line.split()
			if len(l) >= 2:
				line = l[0]
			l = line.strip().split('/')
			if len(l) == 2:
				self.pos[l[0]].append(l[1])
			elif len(l) > 2 and self.allow_unknown != 'FALSE':
				self.pos[l[0]].append(l[2] + '*') # unknown marker
		sys.stderr.write("OK\n")

	def score(self,w,h):
		score_no_match = sys.float_info.max * -1
#		score_no_match = 0
		score_match = self.weight
		pm = self.pos[h[-2]]
		ph = self.pos[h[-1]]
		for i in range(0,len(pm)):
			for j in range(0,len(ph)):
				for r in self.rules:
					if self.matches(r,pm[i],ph[j]):
						return score_match
		return score_no_match

	def matches(self,rule,pm,ph):
		pos_mod = pm.split('(')[0]
		pos_head = ph.split('(')[0]
#		print '{0} = {1}'.format(h[-2],pos_mod)
#		print '{0} = {1}'.format(h[-1],pos_head)

		# NOUN RULES

		if rule == 1:
			return pos_mod == 'VZ' and pos_head == 'N' # PREP + NOUN
		elif rule == 2:
			return pos_mod == 'BW' and pos_head == 'N' # ADV + NOUN
		elif rule == 3:
			return pos_mod == 'N' and pos_head == 'N' # NOUN + NOUN
		elif rule == 4:
			if pos_mod == 'WW' and pos_head == 'N': # VERB + NOUN
				details = pm.split(',')
				if len(details) >= 3:
#					print '----'
					form = details[0].split('(')[1]
					tense = details[1]
					conj = details[2].replace(')','')
#					print form,tense,conj
#					print '----'
					return form == 'pv' and tense == 'tgw' and conj == 'ev'
			return False
		elif rule == 5:
			if pos_mod == 'ADJ' and pos_head == 'N': # ADJ + NOUN
				details = pm.split(',')
				if len(details) >= 3:
					form = details[1]
					infl = details[2]
					return form == 'basis' and infl == 'zonder' # TODO: check whether infl is really important
			return False

		# ADJECTIVE RULES

		elif rule == 6:
			return pos_mod == 'VZ' and pos_head == 'ADJ' # PREP + ADJ
		elif rule == 7:
			return pos_mod == 'N' and pos_head == 'ADJ' # NOUN + ADJ
		elif rule == 8:
			if pos_mod == 'WW' and pos_head == 'ADJ': # VERB + ADJ
				details = pm.split(',')
				if len(details) >= 3:
#					print '----'
					form = details[0].split('(')[1]
					tense = details[1]
					conj = details[2].replace(')','')
#					print form,tense,conj
#					print '----'
					return form == 'pv' and tense == 'tgw' and conj == 'ev'
			return False
		elif rule == 9:
			if pos_mod == 'ADJ' and pos_head == 'ADJ': # ADJ + ADJ
				details = pm.split(',')
				if len(details) >= 3:
					form = details[1]
					infl = details[2]
					return form == 'basis' and infl == 'zonder' # TODO: check whether infl is really important
			return False
		elif rule == 10:
			if pos_mod == 'N' and pos_head == 'WW': # NOUN + PAST PARTICIPLE
				details = ph.split(',')
				form = details[0].replace('WW(','')
				return form == 'vd'
			return False
			
		# VERB RULES -> DANGEROUS

		elif rule == 11:
			return pos_mod == 'VZ' and pos_head == 'WW' # PREP + VERB
		elif rule == 12:
			return pos_mod == 'BW' and pos_head == 'WW' # ADV + VERB
		elif rule == 13:
			if pos_mod == 'ADJ' and pos_head == 'WW':
				details = pm.split(',')
				if len(details) >= 3:
					form = details[1]
					infl = details[2]
					return form == 'basis' and infl == 'zonder' # TODO: check whether infl is really important
			return False

		# QUANTIFIER RULES

		elif rule == 14:
			return pos_mod == 'TW' and pos_head == 'TW' # QUANTIFIER + QUANTIFIER

		else:
			sys.stderr.write("Unknown rule: {0}\n".format(rule))
			sys.exit(1)

	def __repr__(self):
		return 'rules criterion'

class LikeCrit:
	def __init__(self,weight):
		sys.stderr.write("Initializing like criterion with weight={0}... ".format(weight))
		self.weight = weight
		sys.stderr.write("OK\n")

	def score(self,w,h):
#		comp = ''.join(h)
		comp = h[-1]
#		nr_like, w_like = tools.like(w,comp)
		nr_like = len(comp)
		return self.weight * nr_like

	def __repr__(self):
		return 'like criterion'

class MaxHeadCrit:
	def __init__(self,f_counts,weight):
		sys.stderr.write("Initializing max head criterion with file={0} and weight={1}... ".format(f_counts,weight))
		self.counts = tools.load_puni(f_counts)
		self.weight = weight
		sys.stderr.write("OK\n")

	def score(self, w, h):
		return self.weight * self.counts[h[-1]]

	def __repr__(self):
		return 'max head criterion'

class MaxSumCrit:
	def __init__(self,f_counts,weight):
		sys.stderr.write("Initializing highest sum criterion with file={0} and weight={1}... ".format(f_counts,weight))
		self.counts = tools.load_puni(f_counts)
		self.weight = weight
		sys.stderr.write("OK\n")

	def score(self, w, h):
		sum = 0
		for p in h:
			sum += self.counts[p]
		return self.weight * sum

	def __repr__(self):
		return 'highest sum criterion'

class PosCrit:
	def __init__(self,f_pos,weight,allow_unknown):
		sys.stderr.write("Initializing pos criterion with file={0} and weight={1}... ".format(f_pos,weight))
		self.pos = defaultdict(list)
		self.weight = weight
		self.allow_unknown = allow_unknown
#		map = {'LID':'ART','VZ':'PREP','VNW':'PRON','VG':'CONJ','WW':'VERB','BW':'ADV','TW':'NUM','N':'NOUN','ADJ':'ADJ','SPEC':'SPEC','TSW':'INTERJ'}
		for line in open(f_pos,'r'):
			if line.strip().startswith('<s>') or line.strip().startswith('</s>'):
				continue
			# check for counts
			# TODO: use instead of remove
			l = line.split()
			nr = 0
			if len(l) >= 2:
				line = l[0]
				nr = int(l[1])
			l = line.strip().split('/')
			if len(l) == 2:
				self.pos[l[0]].append(l[1])
			elif len(l) > 2 and self.allow_unknown != 'FALSE':
				self.pos[l[0]].append(l[2] + '*') # unknown marker
		sys.stderr.write("OK\n")

	def score(self, w, h):
		score_no_match = sys.float_info.max * -1
#		score_no_match = 0
		score_match = self.weight
		pw = self.pos[w]
		ph = self.pos[h[-1]]
		sys.stderr.write('Comparing word {0} (pos={1}) with hypothesis head {2} (pos={3})\n'.format(w,pw,h[-1],ph))
		for i in range(0,len(pw)):
			for j in range(0,len(ph)):
				if self.allow_unknown == 'TRUE' or (self.allow_unknown == 'HALF' and not ('*' in pw[i] and '*' in ph[j])):
					pw[i] = pw[i].replace('*','')
					ph[j] = ph[j].replace('*','')
				if pw[i] == ph[j]:
					return score_match
		return score_no_match

	def __repr__(self):
		return 'pos criterion'

if __name__ == '__main__':
	if len(sys.argv) < 3:
		sys.stderr.write('Usage: find_best_compound.py <compound-analysis> <criterion>*\n\n')
		sys.stderr.write('Finds the best decompounding for each compound in a given compound analysis, based on the given criteria\n')
		sys.stderr.write("List of possible criteria:\n")
		sys.stderr.write("\t* {0:30}\tFavors the decompounding where the head has the same POS as the compound\n".format("pos=<pos-file>:<weight>"))
		sys.stderr.write("\t* {0:30}\tFavors the decompounding with the highest head count/logprob\n".format("max_head=<count-file>:<weight>"))
		sys.stderr.write("\t* {0:30}\tFavors the decompounding which ressembles the compound the most\n".format("like=<weight>"))
		sys.stderr.write("\t* {0:30}\tFavors the decompounding with the highest sum of counts/logprobs\n".format("max_sum=<count-file>:<weight>"))
		sys.stderr.write("\t* {0:30}\tImplements rules (comma separated or range-based) based on Vandeghinste 2002\n".format("rules=<pos-file>:i,j,k|i-k:weight"))
		sys.exit(1)
	else:
		f = open(sys.argv[1], 'r')
		compounds = defaultdict(list)
		for line in f:
			if '*' in line:
				l = line.strip().split('=')
				w = l[0].split()[1]
				hyp = []
				for el in l[1].split('+'):
					hyp.append(el.split()[0])
#				print 'Adding ' + w + ' -> ' + str(hyp)
				compounds[w].append(hyp)
		f.close()
		crits = []
		for i in range(2,len(sys.argv)):
			crits.append(parseCrit(sys.argv[i]))
		for w in sorted(compounds):
			sys.stderr.write('Working on {0}\n'.format(w))
			max_score = sys.float_info.max * -1
			best = None
			for h in compounds[w]:
				sys.stderr.write('\tScoring {0}\n'.format(h))
				score = 0
				for c in crits:
					sys.stderr.write('\t\t{0}: '.format(c))
					c_score = c.score(w,h)
					sys.stderr.write('score = {0}\n'.format(c_score))
					score += c_score 
				sys.stderr.write('\t\tTOTAL = {0}\n'.format(score))
				if score > 0 and score > max_score:
					best = h
					max_score = score
			if best != None:
	#			print "{0} = {1}".format(w, best)
				print "{0} = {1}".format(w, ' '.join(best))
