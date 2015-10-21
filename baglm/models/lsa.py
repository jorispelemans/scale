from languagemodel import LanguageModel
from gensim import corpora, models, similarities
from collections import deque

class LSA(LanguageModel):

	def __init__(self, file, dictfile, tfidf=None, window=175, gamma=11):
		LanguageModel.__init__(self,file)
		self.history = deque(maxlen=window)
		self.dictfile = dictfile
		self.gamma = gamma
		if tfidf != None:
			self.tfidf = models.TfidfModel.load(tfidf)
		self._readLM()
		self._buildDictionaryIndex()

	def _readLM(self):
		self.dictionary = corpora.Dictionary.load(self.dictfile)
		self.model = models.LsiModel.load(self.file)

	def _buildDictionaryIndex(self):
		def dict_bow():
			for k in self.dictionary.token2id.keys():
				yield self.dictionary.doc2bow([k])
		if self.tfidf != None:
			dict_lsa = self.model[self.tfidf[dict_bow()]]
		else:
			dict_lsa = self.model[dict_bow()]
		self.index = similarities.MatrixSimilarity(list(dict_lsa),num_features=self.model.num_topics)

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
		history_bow = self.dictionary.doc2bow(self.history)
		if self.tfidf != None:
			history_lsa = self.model[self.tfidf[history_bow]]
		else:
			history_lsa = self.model[history_bow]
		sims = self.index[history_lsa]

		try:
			i_word = self.dictionary.token2id.keys().index(word)
		except ValueError:
			return 0
		return self.cos_to_prob(sims, i_word)

	def cos_to_prob(self, cos, index):
		cos_min = min(cos)
		cos_shifted = (cos - cos_min)**self.gamma
		sum_cos_shifted = sum(cos_shifted)
		return cos_shifted[index] / sum_cos_shifted
