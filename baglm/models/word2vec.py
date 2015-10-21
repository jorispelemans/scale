#!/usr/bin/env python

from languagemodel import LanguageModel
from gensim import corpora, models, similarities, matutils
from gensim.models import word2vec
from numpy import array, dot, float32 as REAL
import sys
import math
from scipy.stats import mstats

class Word2Vec(LanguageModel):

	def __init__(self, file, window=175, gamma=11, weights=None):
		LanguageModel.__init__(self,file)
		self.window_size = window
		self.gamma = gamma
		self.weights = weights
		self._readLM()

	def _readLM(self):
		self.model = word2vec.Word2Vec.load_word2vec_format(self.file,binary=True)

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
			return dict([(self.dic[id],self._cut(val)) for id, val in self.tfidf[self.dic.doc2bow(history.split())]])

	def calcProbs(self,history):
		self.model.init_sims()
		if self.weights != None:
			positive = self.weights.getWeights(history).iteritems()
		else:
			positive = [(word, 1.0) for word in history.split()]
		mean = []
		for w, weight in positive:
			if w in self.model.vocab:
				mean.append(weight * matutils.unitvec(self.model.syn0[self.model.vocab[w].index]))
		mean = matutils.unitvec(array(mean).mean(axis=0)).astype(REAL)
		cos = dot(self.model.syn0norm, mean)
		cos_min = min(cos)
		cos_shifted = (cos - cos_min)**self.gamma
		sum_cos_shifted = sum(cos_shifted)
		return cos_shifted / sum_cos_shifted

	def calcProb(self, word, history):
		self.model.init_sims()
		if self.weights != None:
			positive = self.weights.getWeights(history).iteritems()
		else:
			#positive = [(w, 1.0) for w in history.split()]
			positive = [(word, 1.0) for word in history.split()]
		mean = []
		for w, weight in positive:
			if w in self.model.vocab:
				mean.append(weight * matutils.unitvec(self.model.syn0[self.model.vocab[w].index]))
		mean = matutils.unitvec(array(mean).mean(axis=0)).astype(REAL)
#		mean = matutils.unitvec(mstats.gmean(array(mean),axis=0)).astype(REAL)
		sims = dot(self.model.syn0norm, mean)
		try:
			i_word = self.model.vocab[word].index
			prob = self.cosToProb(sims, i_word)
		except KeyError:
			prob = 0 # ignore
		return prob

	def cosToProb(self, cos, index):
		cos_min = min(cos)
		cos_shifted = (cos - cos_min)**self.gamma
		sum_cos_shifted = sum(cos_shifted)
		return cos_shifted[index] / sum_cos_shifted
