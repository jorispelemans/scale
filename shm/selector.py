import sys
import tools
from collections import defaultdict
import logging

class Selector():
	def __init__(self, criteria=None):
		if criteria != None:
			self.criteria = criteria
		else:
			self.criteria = []

	def add_criterion(self, criterion):
		self.criteria.append(criterion)

	def score(self, word, hypothesis):
		score = 0
		for c in self.criteria:
			c_score = c.score(word, hypothesis)
			score += c_score 
		return score

	def select_best_hypothesis(self, word, hypotheses):
		max_score = 0
		best = None
		for h in hypotheses:
			score = self.score(word, h)
			if score > max_score:
				best, max_score = h, score
		return best, max_score

class MaxHeadLengthCriterion:
	def __init__(self, weight):
		logging.info("Initializing max head length criterion with weight={0}... ".format(weight))
		self.weight = weight

	def score(self,w,h):
		return self.weight * len(h[-1])

	def __repr__(self):
		return 'max head length criterion'

class MaxHeadFrequencyCriterion:
	def __init__(self, f_counts, weight):
		logging.info("Initializing max head frequency criterion with file={0} and weight={1}... ".format(f_counts,weight))
		self.counts = {}
		for line in open(f_counts, 'r'):
			w, cnt = line.split()
			self.counts[w] = float(cnt)
		self.weight = weight

	def score(self, w, h):
		return self.weight * self.counts[h[-1]]

	def __repr__(self):
		return 'max head frequency criterion'

class MaxConstituentFrequencyCriterion:
	def __init__(self, f_counts, weight):
		logging.info("Initializing max constituent frequency criterion with file={0} and weight={1}... ".format(f_counts,weight))
		self.counts = {}
		for line in open(f_counts, 'r'):
			w, cnt = line.split()
			self.counts[w] = float(cnt)
		self.weight = weight

	def score(self, w, h):
		sum = 0
		for p in h:
			sum += self.counts[p]
		return self.weight * sum

	def __repr__(self):
		return 'max constituent frequency criterion'
