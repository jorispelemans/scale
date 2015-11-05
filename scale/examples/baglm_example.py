#!/usr/bin/env python

"""
USAGE: baglm_example.py TEST_CORPUS [VOCABULARY_SIZE]

BagLM example that calculates (log)probabilities based on the following 3 models:
1) LSA-based language model
2) Word2Vec-based language model
3) Cache language model

The models are trained on a Dutch wikipedia corpus (132MB @ 2015/10/14 18:45) with a given vocabulary size.
Time (on Intel i5-2400) and storage needed for training models with different vocabulary sizes:
voc	time		storage
5k	16 mins		101 MB
10k	17 mins		118 MB	
25k	17 mins		154 MB
50k	18 mins		191 MB
100k	19 mins		252 MB

Example: python baglm_example.py test.txt 10000
"""

import os
import logging
import sys
import urllib
from math import log10
from gensim.corpora import WikiCorpus, SvmLightCorpus
from gensim.models import TfidfModel, LsiModel, Word2Vec
from scale.baglm import models
from scale import util

DEFAULT_VOC_SIZE = 25000

if __name__ == '__main__':
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
	logging.root.setLevel(level=logging.INFO)

	# ARGUMENT PARSING
	if len(sys.argv) < 2:
		print globals()['__doc__'] % locals()
		sys.exit(1)
	f_test_corpus = sys.argv[1]
	if len(sys.argv) > 2:
		voc_size = int(sys.argv[2])
	else:
		voc_size = DEFAULT_VOC_SIZE

	# SETTINGS

	# training corpus
	prefix = "wiki"
	f_corpus = prefix + ".bz2"
	
	# model parameters and output
	lsa_dim = 100
	w2v_dim = 50
	f_docs = prefix + ".docs"
	f_bow = "{0}_voc{1}.bow".format(prefix, voc_size)
	f_tfidf = "{0}_voc{1}.tfidf".format(prefix, voc_size)
	f_lsa = "{0}_voc{1}_dim{2}.lsa".format(prefix, voc_size, lsa_dim)
	f_dict = "{0}_voc{1}.dict".format(prefix, voc_size)
	f_w2v = "{0}_voc{1}_dim{2}_win5.bin".format(prefix, voc_size, w2v_dim)

	# CORPUS PREPROCESSING

	# download wikipedia training corpus (2015/10/14 18:45, 132MB)
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

	# filter dictionary
	wiki.dictionary.filter_extremes(no_below=0, no_above=1, keep_n=voc_size)
	wiki.dictionary.save(f_dict)

	# raw bag-of-words model
	if not os.path.exists(f_bow):
		SvmLightCorpus.serialize(f_bow, wiki)
	bow = SvmLightCorpus(f_bow)

	# tf-idf model
	if os.path.exists(f_tfidf):
		tfidf = TfidfModel.load(f_tfidf)
	else:
		tfidf = TfidfModel(bow, id2word=wiki.dictionary)
		tfidf.save(f_tfidf)

	# TRAINING

	# lsa model
	if not os.path.exists(f_lsa):
		lsa = LsiModel(tfidf[bow], id2word=wiki.dictionary, num_topics=lsa_dim)
		lsa.save(f_lsa)

	# word2vec model
	class MyCorpus():
		def __iter__(self):
			for d in wiki.get_texts():
				yield [w for w in d if w in wiki.dictionary.token2id]
	if not os.path.exists(f_w2v):
		w2v = Word2Vec(MyCorpus(), size=w2v_dim, min_count=1, window=5)
		w2v.save_word2vec_format(f_w2v, binary=True)

	# LANGUAGE MODELS
	lm_cache = models.Cache(window=50)
	lm_lsa = models.LSA(f_lsa, f_dict, tfidf=f_tfidf, window=50)
	lm_w2v = models.Word2Vec(f_w2v, window=50)

	# EVALUATION

	# interpolation weights
	lms = [(lm_cache, 0.2), (lm_lsa, 0.4), (lm_w2v, 0.4)]

	# calculate probabilities
	for i, line in enumerate(open(f_test_corpus, 'r')):
		print "{0}) {1}".format(i+1, line.strip())
		for word in line.strip().split(' '):
			prob = 0
			for lm, weight in lms:
				prob += weight * lm.calc_prob(word)
				lm.add_to_history(word)
			if prob != 0:
				logprob = log10(prob)
			else:
				logprob = float("-inf")
			print "\tLOGP({0}) = {1:.7f} [{2}]".format(word, logprob , prob)
