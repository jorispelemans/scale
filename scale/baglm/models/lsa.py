"""
Module that calculates the probability of a word given the previous word.
The probability calculation is based on Latent Semantic Analysis i.e. the distance 
between the word and the previous words in a semantic space calculated using singular value decomposition.
"""

from collections import deque
from gensim import corpora, models, similarities, matutils
from numpy import log, exp

class LSA():

	def __init__(self, f, dictfile, tfidf=None, window=175, gamma=11):
		self.f = f
		self.dictfile = dictfile
		if tfidf != None:
			self.tfidf = models.TfidfModel.load(tfidf)
		self._readLM()
		self._buildDictionaryIndex()
		self.window = window
		self.gamma = gamma
		self.init_history()

	def _readLM(self):
		self.dictionary = corpora.Dictionary.load(self.dictfile)
		self.model = models.LsiModel.load(self.f)

	def _buildDictionaryIndex(self):
		def dict_bow():
			for k in self.dictionary.token2id.keys():
				yield self.dictionary.doc2bow([k])
		if self.tfidf != None:
			dict_lsa = self.model[self.tfidf[dict_bow()]]
		else:
			dict_lsa = self.model[dict_bow()]
#		self.index = similarities.MatrixSimilarity(list(dict_lsa),num_features=self.model.num_topics)
		terms = matutils.Dense2Corpus(self.model.projection.u.T)
		self.index = similarities.MatrixSimilarity(terms, num_features=self.model.num_topics)

	def init_history(self, history=[]):
		self.history = deque(history, maxlen=self.window)

	def add_to_history(self, word):
		self.history.append(word)

	def calc_prob(self, word, history=None):
		probs = self.calc_probs(history)
		try:
			i_word = self.dictionary.token2id.keys().index(word)
			return probs[i_word][1]
		except ValueError:
			return 0

	def calc_probs(self, history=None, sort=False):
		if history != None:
			self.init_history(history)
		if len(self.history) == 0:
			return [(k,0) for k in self.dictionary.token2id]
		history_bow = self.dictionary.doc2bow(self.history)
		if self.tfidf != None:
			history_lsa = self.model[self.tfidf[history_bow]]
		else:
			history_lsa = self.model[history_bow]
		sims = self.index[history_lsa]
		try:
			probs = self.cos_to_probs(sims)
		except FloatingPointError:
			return [(k,0) for k in self.dictionary.token2id]
		assert abs(1 - sum(probs)) < 1e-7
		if sort:
			return sorted(enumerate(probs), key=lambda item: -item[1])
		else:
			return list(enumerate(probs))

	def cos_to_probs(self, cos):
		cos_min = min(cos)
		#cos_shifted = (cos - cos_min)**self.gamma
		cos_shifted = exp(log(cos - cos_min) * log(self.gamma))
		sum_cos_shifted = sum(cos_shifted)
		if sum_cos_shifted == 0:
			raise FloatingPointError('Division by zero')
		return cos_shifted / sum_cos_shifted

	def __repr__(self):
		return "LSA(window=%s, gamma=%s)" % \
			(self.window, self.gamma)
