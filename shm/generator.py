import re
import sys
import commands
from collections import defaultdict
import logging

def isupper(w):
	return w.isupper() and "'" not in w

class Generator():

	dutch_prefixes = ["on", "wan"]
	dutch_bind_morphemes = ["s", "en", "-"]

	def __init__(self, lex_mod, lex_head, minlen_mod=1, minlen_head=1, minlen_comp=1, prefixes=None, bind_morphemes=None):
		self.lex_mod = lex_mod
		self.lex_head = lex_head
		self.minlen_mod = minlen_mod
		self.minlen_head = minlen_head
		self.minlen_comp = minlen_comp
		self.prefixes = prefixes
		self.bind_morphemes = bind_morphemes

	def decompound(self, word):
		return self._decompound(word)

	def _decompound(self, w, pos=1, history=[]):
#		logging.debug("Decompounding {0} from position {1}: {2}".format(w, pos, w[pos-1:]))
		res = []
		if len(w) < self.minlen_comp:
			logging.debug('{0} too short to decompound'.format(w))
		else:
			for i in range(pos,len(w)):
				w1 = w[pos-1:i]
				w2 = w[i:]
				# 1) find a candidate left constituent
				i1 = self._inflect(w1)
				if i1 != '':
					logging.debug("Found left constituent at position {0} => {1}".format(i, " + ".join(history+[i1,"..."])))
					# 2) find a candidate right constituent
					# 2a) w2 is a valid right constituent
					i2 = self._inflect(w2,'>')
					if (i2 != ''):
						hist = history + [i1, i2]
						logging.debug("\tAdding candidate hypothesis: {0}".format(hist))
						#yield history + i1 + i2
						res.append(hist)
					# 2b) w2 is itself a compound => recursion
					hist = history + [i1]
					right = self._decompound(w, i+1, hist)
					if len(right) != 0:
						res += right
					else:
						logging.debug("\tNo right constituents found, aborting hypothesis")
		return res

	def _inflect(self, word,pos='<'):
		w = ''
		code = ''
		if pos == '<':
			if len(word)>=2 and (isupper(word) or (isupper(word[0:-1]) and word[-1] == '-')):
				w = word.replace('-','')
				code = 'ACRO'
			elif len(word) < self.minlen_mod:
				return ''
		elif len(word) < self.minlen_head:
			return ''
		if pos == '<':
			lex = self.lex_mod
		else:
			lex = self.lex_head
		if word in lex:
			w = word
			code = 'LEX'
		elif (pos != '>'):
			for r in self.bind_morphemes:
				if (word.endswith(r)) and word[:-len(r)] in lex:
					w = word[:-len(r)]
					code = 'INFL:' + r
		if w != '':
			return '%s (%s)' % (w,code)
		return ''
