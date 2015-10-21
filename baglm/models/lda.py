#!/usr/bin/env python

from languagemodel import LanguageModel
from gensim import corpora, models, similarities

class LDA(LanguageModel):

	def __init__(self, file, dictfile, tfidf=None, window=175, gamma=11):
		LanguageModel.__init__(self,file)
		self.dictfile = dictfile
		self.window_size = window
		self.gamma = gamma
		if tfidf != None:
			self.tfidf = models.TfidfModel.load(tfidf)
		else:
			self.tfidf = None
		self._readLM()
		self._buildDictionaryIndex()

	def _readLM(self):
		print 'reading term-topic matrix from file ' + self.file
		self.dictionary = corpora.Dictionary.load(self.dictfile)
		self.model = models.LdaModel.load(self.file)

	def _buildDictionaryIndex(self):
		# Another possibility is to use the rows of the lsa to convert words to latent space (more correct and probably faster, but deeper into gensim code) TODO
		def dict_bow():
			for k in self.dictionary.token2id.keys():
				yield self.dictionary.doc2bow([k])
		if self.tfidf != None:
			dict_lda = self.model[self.tfidf[dict_bow()]]
		else:
			dict_lda = self.model[dict_bow()]
		self.index = similarities.MatrixSimilarity(list(dict_lda),num_features=self.model.num_topics)
		#self.index = similarities.Similarity('dump',dict_lda,num_features=self.model.num_topics)

	def calcProb(self, word, history):
		history_bow = self.dictionary.doc2bow(history.split())
		if self.tfidf != None:
			history_lda = self.model[self.tfidf[history_bow]]
		else:
			history_lda = self.model[history_bow]
		sims = self.index[history_lda]

		try:
			i_word = self.dictionary.token2id.keys().index(word)
		except ValueError:
			return 0
		return self.cosToProb(sims, i_word)

	def cosToProb(self, cos, index):
		cos_min = min(cos)
		cos_shifted = (cos - cos_min)**self.gamma
		sum_cos_shifted = sum(cos_shifted)
		return cos_shifted[index] / sum_cos_shifted
