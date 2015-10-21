from gensim import corpora, models, similarities
import math
from collections import defaultdict, deque
	
class Cache():

	(LIN_DECAY, EXP_DECAY, EXP_DECAY_CCS) = ('lin','exp','exp_ccs')

	def __init__(self, window=400, decay=EXP_DECAY_CCS, alpha=0.99):
		self.history = deque(maxlen=window)
		self.decay = decay
		self.alpha = alpha
		self.cache = defaultdict(float)

	def init_history(self, history):
		maxlen = self.history.maxlen
		self.history = deque(history, maxlen=maxlen)
		self._update()

	def add_to_history(self, word):
		self.history.append(word)
		self._update()

	def _update(self):
		self.cache = defaultdict(float)
		size = len(self.history)
		total = 0
		for i, word in enumerate(self.history):
			if self.decay == self.LIN_DECAY:
				contribution = size - (1 - self.alpha) * (size - float(i)) #linear decay
			elif self.decay == self.EXP_DECAY:
				contribution = math.exp(-1*(1-self.alpha)*(size-i)) #clarkson & robinson
			elif self.decay == self.EXP_DECAY_CCS:
				contribution = math.pow(self.alpha,(size-i)) #bellegarda style = simpler and almost identical
			else:
				contribution = 1 # no decay = uniform cache
			self.cache[word] += contribution
			total += contribution
		if total != 0:
			for k in self.cache:
				self.cache[k] /= total

	def calc_prob(self, word, history=None):
		if history != None:
			self.init_history(history)
		if len(self.history) == 0:
			return 0
		try:
			return self.cache[word]
		except(KeyError):
			return 0
