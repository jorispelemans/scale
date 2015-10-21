import re
import sys
import commands
from collections import defaultdict

DEBUG = False
def info(s):
	if DEBUG:
		sys.stderr.write(str(s) + '\n')

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

	def _decompound(self, w, orig=None, info_pre=''):
		if orig == None:
			orig =w
		r = []
		info(info_pre + 'Decompounding ' + w + ':')
		info_pre_old = info_pre
		info_pre = info_pre + '\t'
		if len(w) < self.minlen_comp:
			info(info_pre + w + ' too short to decompound')
		else:
			for i in range(1,len(w)):
				w1 = w[:i]
				w2 = w[i:]
				i1 = self._inflect(w1, info_pre=info_pre)
				if (i1 != ''):
					if (orig.endswith(w2)):
						i2 = self._inflect(w2,'>', info_pre)
					else:
						i2 = self._inflect(w2, info_pre=info_pre)
					if (i2 != ''):
						r.append([i1,i2])
					i2 = self._decompound(w2,orig,info_pre+'\t')
					if (i2 != []):
						r.append([i1,i2])
		if r != []:
			info(info_pre_old + 'Decompounding ' + w + ' succesful')
		else:
			info(info_pre_old + 'Decompounding ' + w + ' unsuccesful')
		return r

	def _inflect(self, word,pos='<',info_pre=''):
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
			info(info_pre + word + ' in lexicon')
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
