#!/usr/bin/env python

from gensim import corpora, models, similarities
import math
from collections import defaultdict
	
# TODO
# n-gram caches
# exponential decay symmetric around w_(q-i) s.t. the previous word gets a lower weight 

class Cache():

	(LIN_DECAY, EXP_DECAY, EXP_DECAY_CCS) = ('lin','exp','exp_ccs')

	def __init__(self, window=400, decay=EXP_DECAY_CCS, alpha=1):
		self.cache = {}
		self.window_size = window
		self.decay = decay
		self.alpha = alpha
	
	# interpretation alpha: the lower, the more decay; with alpha=1 every word has equal contribution
	def buildCache(self,window):
		#h = history.split()
		#size = len(h)
		size = len(window)
		self.cache = defaultdict(int)
		sum = float(0)
		for i, word in enumerate(window):
			if self.decay == self.LIN_DECAY:
				contribution = size - (1 - self.alpha) * (size - float(i)) #linear decay
			elif self.decay == self.EXP_DECAY:
				contribution = math.exp(-1*(1-self.alpha)*(size-i)) #clarkson & robinson
			elif self.decay == self.EXP_DECAY_CCS:
				contribution = math.pow(self.alpha,(size-i)) #bellegarda style = simpler and almost identical
			else:
				contribution = 1 # no decay = uniform cache
			self.cache[word] += contribution
			sum += contribution
		if sum != 0:
			for k in self.cache:
				self.cache[k] /= sum

	def calcProb(self, word, history=None):
		try:
			return self.cache[word]
		except(KeyError):
			return 0
