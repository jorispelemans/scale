#!/usr/bin/env python

"""
USAGE: baglm_example.py TEST_CORPUS [VOCABULARY_SIZE] [TRAINING_CORPUS]

BagLM example that calculates (log)probabilities for words in a given test corpus, based on the following 3 models:
1) LSA-based language model, trained with a vocabulary of given size
2) Word2Vec-based language model, trained with a vocabulary of given size
3) Cache language model

You can specify your own training corpus in which case each line in the corpus will correspond to a document.
If no training corpus is specified, the models are trained on a Dutch wikipedia corpus (132MB @ 2015/10/14 18:45).
Time (on Intel i5-2400, using blas and cython) and storage needed for training Wikipedia models with different vocabulary sizes:
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
from gensim.corpora import WikiCorpus, TextCorpus
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

	wiki = True
	if len(sys.argv) > 3:
		wiki = False
		f_corpus = sys.argv[3]
		if os.path.exists(f_corpus):
			prefix = os.path.basename(f_corpus)
		else:
			sys.stderr.write("Specified training corpus does not exist: {0}\n".format(f_corpus))
			sys.exit(1)
	else:
		prefix = "wiki"
		f_corpus = prefix + ".bz2"

	# SETTINGS

	# model parameters and output
	lsa_dim = 100
	w2v_dim = 50
	f_bow = "{0}.bow".format(prefix)
	f_tfidf = "{0}_voc{1}.tfidf".format(prefix, voc_size)
	f_lsa = "{0}_voc{1}_dim{2}.lsa".format(prefix, voc_size, lsa_dim)
	f_dict = "{0}_voc{1}.dict".format(prefix, voc_size)
	f_w2v = "{0}_voc{1}_dim{2}_win5.bin".format(prefix, voc_size, w2v_dim)

	# CORPUS PREPROCESSING

	if wiki: # models will be trained on the Dutch Wikipedia corpus
		if os.path.exists(f_bow):
			corpus = WikiCorpus.load(f_bow)
		else:
			# download wikipedia training corpus (2015/10/14 18:45, 132MB)
			if not os.path.exists(f_corpus):
				if raw_input("About to download Dutch Wikipedia corpus (132MB @ 2015/10/14 18:45). Do you want to proceed? (y/n) ").startswith("y"):
					util.download_file("https://dumps.wikimedia.org/nlwiki/latest/nlwiki-latest-pages-articles1.xml.bz2", f_corpus, progress=True)
				else:
					sys.exit()
			corpus = WikiCorpus(f_corpus)
			corpus.save(f_bow)
	else: # models will be trained on your own corpus
		if os.path.exists(f_bow):
			corpus = TextCorpus.load(f_bow)
		else:
			corpus = TextCorpus(f_corpus)
			corpus.save(f_bow)

	# filter dictionary
	corpus.dictionary.filter_extremes(no_below=0, no_above=1, keep_n=voc_size)
	corpus.dictionary.save(f_dict)

	# tf-idf model
	if os.path.exists(f_tfidf):
		tfidf = TfidfModel.load(f_tfidf)
	else:
		tfidf = TfidfModel(corpus, id2word=corpus.dictionary)
		tfidf.save(f_tfidf)

	# TRAINING

	# lsa model
	if not os.path.exists(f_lsa):
		lsa = LsiModel(tfidf[corpus], id2word=corpus.dictionary, num_topics=lsa_dim)
		lsa.save(f_lsa)

	# word2vec model
	class MyCorpus():
		def __iter__(self):
			for d in corpus.get_texts():
				yield [w for w in d if w in corpus.dictionary.token2id]
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
