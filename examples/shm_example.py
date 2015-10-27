from shm import *
import sys
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
#logging.root.setLevel(level=logging.DEBUG)
logging.root.setLevel(level=logging.INFO)

f_wlist = "celex_5k.wlist"
f_mods_lex = "med_600k.wlist"
f_heads_lex = "med_200k.wlist"

logging.info("Reading heads lexicon {0}... ".format(f_heads_lex))
heads_lex = set()
for line in open(f_heads_lex,'r'):
	heads_lex.add(line.strip())
logging.info("%i entries" % len(heads_lex))

logging.info("Reading mods lexicon {0}... ".format(f_mods_lex))
mods_lex = set()
for line in open(f_mods_lex,'r'):
	mods_lex.add(line.strip())
logging.info("%i entries" % len(mods_lex))

# Generate all possible decompoundings
g = Generator(mods_lex, heads_lex, minlen_mod=3, minlen_head=4, prefixes=Generator.dutch_prefixes, bind_morphemes=Generator.dutch_bind_morphemes)
generated_hypotheses = {}
for cnt, line in enumerate(open(f_wlist, 'r')):
	w = line.strip()
	d = g.decompound(w)
	if len(d) != 0:
		generated_hypotheses[w] = d
logging.info('{0}/{1} possible compound(s) found'.format(len(generated_hypotheses), cnt))

# Select best semantic head hypothesis
s = Selector()
s.add_criterion(MaxHeadLengthCriterion(1.0))
for w in generated_hypotheses:
	logging.info('Selection for word {0}:'.format(w))
	d = generated_hypotheses[w]
	for i, h in enumerate(d):
		logging.info('\t{0}) {1}'.format(i, h))
	best, score = s.select_best_hypothesis(w, d)
	logging.info('\t==> Best hypothesis is {0} with score {1}'.format(best, score))
