#!/usr/bin/env python

class LanguageModel():

	def __init__(self, file):
		self.file = file

	def calcProb(self, word, history):
		raise NotImplementedError('must override calcProb()')
