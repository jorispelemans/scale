from baglm import models
from math import log10

def test_cache():
	corpus = "een eerste test"
	cache = models.Cache(window=2)
	for w in corpus.split():
		cache.add_to_history(w)
		print cache.cache


# load models (TODO: use reasonable parameter values)

voc_size = 25000
lsa_dim = 100
w2v_dim = 50

cache = models.Cache(window=50)
lsa = models.LSA("dest.utf8_voc{0}_docsize30_topics{1}.tfidf.lsi".format(voc_size, lsa_dim), "dest.utf8_voc{0}.dict".format(voc_size), tfidf="dest.utf8_voc{0}_docsize30.tfidf".format(voc_size), window=50)
w2v = models.Word2Vec("dest.utf8_voc{0}_dim{1}_win5.bin".format(voc_size, w2v_dim), window=50)
lms = [(cache, 0.2), (lsa, 0.4), (w2v, 0.4)]

# test corpus
corpus = ["een eerste test", "een tweede test"]

# calculate probabilities

for i, line in enumerate(corpus):
	print "{0}) {1}".format(i+1, line.strip())
	for word in line.split(' '):
		prob = 0
		for lm, weight in lms:
			prob += weight * lm.calc_prob(word)
			lm.add_to_history(word)
		if prob != 0:
			logprob = log10(prob)
		else:
			logprob = float("-inf")
		print "\tLOGP({0}) = {1:.7f} [{2}]".format(word, logprob , prob)
