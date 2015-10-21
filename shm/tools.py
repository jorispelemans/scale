#! /usr/bin/env python

#from gensim import corpora, models, similarities, matutils
from collections import defaultdict
import sys, os, re, string, commands

path_cornetto = '/users/spraak/jpeleman/docs/lm/semantics/synsem/cornetto/'

def load_ewn():
	f = open(path_cornetto + 'D08/etc/examples','r')
	ewn = defaultdict(list)
	top_level_words = ['iets','gebeurde','entiteit']#,'ding','voorwerp']

	f_level1 = open('/users/spraak/jpeleman/docs/lm/semantics/synsem/full_analysis/ewn_level1','r')
	level1 = []
	for l in f_level1:
		level1.append(l.strip())
	f_level1.close()

#	print level1

	senses = defaultdict(int)

	for line in f:
		l = line.strip().split()
		dist = l[0]
		w1 = re.sub('#.*','',l[1])
		sense = l[1][string.find(l[1],'#'):]

		if int(sense[1:]) > senses[w1]:
			senses[w1] = int(sense[1:])

		w2 = re.sub('#.*','',l[2])
	#	if True:
#		if dist == '11' and w2 not in top_level_words and sense == '#1':
#		print 'L2: ' + l[2] 
		if dist == '11' and w2 not in top_level_words and sense == '#1' and l[2] not in level1:
			ewn[w1].append(w2)
		#TODO: write to stderr which are ignored

	#print hypernyms['parhelium']

	f.close()
	return ewn, senses

def load_puni(puni):
	# reading punis
	f = open(puni,'r')

	logprobs = {}

	if puni.endswith(".cnt"):
		header_read = True
	else:
		header_read = False
	for line in f:
		if (not header_read):
			if (line.strip() == '#'):
				header_read = True
		else:
			l = line.strip().split()
			cand = l[0]
			logprob = float(l[1])
			logprobs[cand] = logprob
			
	f.close()
	return logprobs

def load_cands(cand_file,logprobs,logprob_min,logprob_max):
	f = open(cand_file,'r')

	cands = []

	for line in f:
		cand = line.strip().split()[0]
		logprob = logprobs[cand]
		if logprob > logprob_min and logprob < logprob_max:
			cands.append(cand)
			
	f.close()
	return cands

def load_cands_old(cand_file,logprob_min,logprob_max):
	f = open(cand_file,'r')

	cands = []

	for line in f:
		l = line.strip().split()
		cand = l[0]
		logprob = float(l[1])
		if logprob > logprob_min and logprob < logprob_max:
			cands.append(cand)
			
	f.close()
	return cands

def morph3(cand_file, puni):
	#decomp_out = '/users/spraak/jpeleman/docs/lm/semantics/synsem/decompounding/' + 'temp'
	#decomp_out = '/users/spraak/jpeleman/docs/lm/semantics/synsem/full_analysis/morph3'
	#decomp_out = '/users/spraak/jpeleman/docs/lm/semantics/synsem/full_analysis/morph3_all'
	decomp_out = '/users/spraak/jpeleman/docs/lm/semantics/synsem/full_analysis/morph3_80k'
	if not os.path.exists(decomp_out):
		cmd = '/users/spraak/jpeleman/docs/lm/semantics/synsem/decompounding.py ' + ('.').join(cand_file.split('.')[0:2]) + ' ' + puni + ' > ' + decomp_out
		sys.stderr.write(cmd + '\n')
		os.system(cmd)
	f = open(decomp_out, 'r')
	morph3 = defaultdict(list)
	for line in f:
		if '*' in line:
			l = line.strip().split('+')
			w = l[0].split()[1]
			hyp = l[-1].split()[0]
	#		print 'Adding ' + w + ' -> ' + hyp
			morph3[w].append(hyp)
	f.close()
	return morph3

def load_lsa(model):
	#model='/users/spraak/jpeleman/docs/lm/semantics/results/dest_3_xxx_filter_eos_sos_min5_sss_topics100.lsi'
	#model='/users/spraak/jpeleman/docs/lm/semantics/results/dest_3_normal2_xxx_filter_eos_sos_min5_sss_topics100.lsi'
	model='/users/spraak/jpeleman/docs/lm/semantics/results/med_3_xxx_filter_eos_sos_min5_normal2_sss_topics100.lsi'
	#model='/users/spraak/jpeleman/docs/lm/semantics/results/dest_4_xxxx_filter_eos_sos_min3_sss_topics100.lsi'
	exp = os.path.splitext(model)[0]
	parts = exp.split('_')
	base = '_'.join(parts[0:len(parts)-1])
	# loading dictionary, bow and model
	dictionary = corpora.Dictionary.load(base + '.dict')
	#print dictionary.token2id
	bow = corpora.MmCorpus(exp + '.mm')
	#tfidf = models.TfidfModel.load(exp + '.tfidf')
	#corpus_tfidf = tfidf[bow]
	lsi = models.LsiModel.load(model)
	#print "Checking existence of similarity index"
	if(os.path.exists(model + '.index')):
	#	print "Index found. Loading..."
		index = similarities.MatrixSimilarity.load(model + '.index')
	else:
	#	print "No index found. Creating and saving..."
		#TODO: use the memory efficient version of this
		#index = similarities.MatrixSimilarity(lsi[bow])
		terms=matutils.Dense2Corpus(lsi.projection.u.T) 
		index = similarities.MatrixSimilarity(terms)
		index.save(model + '.index')
	return lsi, dictionary, index

def pos_art(word):
	cmd = 'grep "^' + word + '/" ~/docs/lm/semantics/synsem/full_analysis/posart_80k'
	out = commands.getoutput(cmd)
	if out != '':
		res = out.strip().split('/')[-1]
		return res 
	return ''

def pos_art_old(word):
	return commands.getoutput(path_cornetto + "POS_ART \"" + word + "\"").strip()

def query_lsa(lsi,dictionary,index,query,sim_thr):
	results = []
	vec_bow = dictionary.doc2bow(query.split())
	vec_lsi = lsi[vec_bow]
	# calculate and print similarities
	id2token = dict((v,k) for k,v in dictionary.token2id.iteritems())
	sims = index[vec_lsi]
	sims = sorted(enumerate(sims), key=lambda item: -item[1])
	for idother, sim in sims[1:50]:
		if sim < sim_thr or (sim == 1.0):
			break
		h = id2token[idother]
		results.append(h)
	return results

def like(cand,h):
#	prefixes = ['on','wan','ver','bij']
#	for p in prefixes:
#		if (cand == p + h) or (h == p + cand):
#			return min(len(h),len(cand))
	res = []
	min = 4
	for i in range(len(cand)-min+1):
		for j in range(i+min,len(cand)+1):
			s = cand[i:j]
			if string.find(h,s) != -1:
				res.append(s)
	max=0
	best = ''
	for s in res:
		if len(s) > max:
			max = len(s)
			best = s
	return max, best
