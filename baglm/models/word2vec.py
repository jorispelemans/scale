"""
Module that calculates the probability of a word given the previous word.
The probability calculation is based on Word2Vec i.e. the distance 
between the word and the previous words in a semantic space calculated using the continuous skip-gram model [1].

[1] Tomas Mikolov, Kai Chen, Greg Corrado, and Jeffrey Dean. Efficient Estimation of Word Representations in Vector Space. In Proceedings of Workshop at ICLR, 2013.
"""

from gensim import corpora, models, matutils
from gensim.models import word2vec
from numpy import array, dot, float32 as REAL
from collections import deque

class Word2Vec():

	def __init__(self, f, window=175, gamma=11, weights=None):
		self.f = f
		self.history = deque(maxlen=window)
		self.gamma = gamma
		self.weights = weights
		self._readLM()

	def _readLM(self):
		self.model = word2vec.Word2Vec.load_word2vec_format(self.f,binary=True)

	class TfidfWeights():

		def __init__(self, tfidf, dic, thr=0.0):
			self.tfidf = models.TfidfModel.load(tfidf)
			self.dic = corpora.Dictionary.load(dic)
			self.thr = thr

		def _cut(self,val):
			if val < self.thr:
				return 0
			else:
				return val

		def getWeights(self, history):
			return dict([(self.dic[id],self._cut(val)) for id, val in self.tfidf[self.dic.doc2bow(history)]])

	def init_history(self, history):
		maxlen = self.history.maxlen
		self.history = deque(history, maxlen=maxlen)

	def add_to_history(self, word):
		self.history.append(word)

	def calc_prob(self, word, history=None):
		if history != None:
			self.init_history(history)
		if len(self.history) == 0:
			return 0
		self.model.init_sims()
		if self.weights != None:
			positive = self.weights.getWeights(self.history).iteritems()
		else:
			positive = [(word, 1.0) for word in self.history]
		mean = []
		for w, weight in positive:
			if w in self.model.vocab:
				mean.append(weight * matutils.unitvec(self.model.syn0[self.model.vocab[w].index]))
		mean = matutils.unitvec(array(mean).mean(axis=0)).astype(REAL)
		sims = dot(self.model.syn0norm, mean)
		try:
			i_word = self.model.vocab[word].index
			prob = self.cos_to_prob(sims, i_word)
		except KeyError:
			prob = 0 # ignore
		return prob

	def cos_to_prob(self, cos, index):
		cos_min = min(cos)
		cos_shifted = (cos - cos_min)**self.gamma
		sum_cos_shifted = sum(cos_shifted)
		return cos_shifted[index] / sum_cos_shifted
