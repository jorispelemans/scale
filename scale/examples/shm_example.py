#!/usr/bin/env python

"""
USAGE: shm_example.py WLIST [MODIFIER_LEXICON_SIZE] [HEAD_LEXICON_SIZE]

	Semantic Head Mapping example that finds semantic heads for a given word list in 2 steps:
	1) Generation: generate candidate decompoundings from modifier and head lexica
	2) Selection: find best hypothesis based on a maximum head length criterion

	The lexica contain the most frequent words in a Dutch wikipedia corpus (132MB @ 2015/10/14 18:45). 

Example: python shm_example.py test.wlist 100000 30000
"""

import logging
import os
import urllib
import sys
from gensim.corpora import WikiCorpus
from scale.shm import *
from scale import util

DEFAULT_MODS_SIZE = 600000
DEFAULT_HEADS_SIZE = 200000

if __name__ == '__main__':
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
	logging.root.setLevel(level=logging.INFO)

	# ARGUMENT PARSING
	if len(sys.argv) < 2:
		print globals()['__doc__'] % locals()
		sys.exit(1)
	f_wlist = sys.argv[1]
	if len(sys.argv) > 2:
		nr_mods = int(sys.argv[2])
	else:
		nr_mods = DEFAULT_MODS_SIZE
	if len(sys.argv) > 3:
		nr_heads = int(sys.argv[3])
	else:
		nr_heads = DEFAULT_HEADS_SIZE

	# CORPUS PREPROCESSING
	prefix = "wiki"
	f_corpus = prefix + ".bz2" 
	f_docs = prefix + ".docs"

	# download wikipedia training corpus (132MB @ 2015/10/14 18:45)
	if os.path.exists(f_docs):
		wiki = WikiCorpus.load(f_docs)
	else:
		if not os.path.exists(f_corpus):
			if raw_input("About to download Dutch Wikipedia corpus (132MB @ 2015/10/14 18:45). Do you want to proceed? (y/n) ").startswith("y"):
				util.download_file("https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-pages-articles1.xml.bz2", f_corpus, progress=True)
			else:
				sys.exit()
		wiki = WikiCorpus(f_corpus)
		wiki.save(f_docs)

	# creating modifier and head lexicon
	heads = set()
	mods = set()
	for i, token in enumerate(token for token, tokenid in sorted(wiki.dictionary.token2id.iteritems(), key=lambda x: wiki.dictionary.dfs[x[1]], reverse=True)):
		if i <= nr_heads:
			heads.add(token)
		if i <= nr_mods:
			mods.add(token)
		if i >= max(nr_heads, nr_mods):
			break

	logging.info("Generating all possible decompoundings")
	g = Generator(mods, heads, minlen_mod=4, minlen_head=4, prefixes=Generator.dutch_prefixes, bind_morphemes=Generator.dutch_bind_morphemes)
	generated_hypotheses = {}
	for cnt, line in enumerate(open(f_wlist, 'r')):
		w = line.strip()
		d = g.decompound(w)
		if len(d) != 0:
			generated_hypotheses[w] = d
	logging.info('{0}/{1} possible compound(s) found'.format(len(generated_hypotheses), cnt))

	logging.info("Selecting best semantic head hypothesis")
	s = Selector()
	s.add_criterion(MaxHeadLengthCriterion(1.0))
	for w in generated_hypotheses:
		logging.info('Selection for word {0}:'.format(w))
		d = generated_hypotheses[w]
		for i, h in enumerate(d):
			logging.info('\t{0:2}) {1:40} score = {2}'.format(i+1, h, s.score(w, h)))
		best, score = s.select_best_hypothesis(w, d)
		logging.info('\t==> Semantic head = {0}'.format(best[-1]))
