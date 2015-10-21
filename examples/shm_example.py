import shm
import sys


f_wlist = "celex_5k.wlist"
f_mods_lex = "med_600k.wlist"
f_heads_lex = "med_200k.wlist"

sys.stderr.write("Reading heads lexicon {0}... ".format(f_heads_lex))
heads_lex = set()
for line in open(f_heads_lex,'r'):
	heads_lex.add(line.strip())
sys.stderr.write("%i entries\n" % len(heads_lex))

sys.stderr.write("Reading mods lexicon {0}... ".format(f_mods_lex))
mods_lex = set()
for line in open(f_mods_lex,'r'):
	mods_lex.add(line.strip())
sys.stderr.write("%i entries\n" % len(mods_lex))

# Generate all possible decompoundings
g = shm.Generator(mods_lex, heads_lex, minlen_mod=1, minlen_head=1, minlen_comp=1, prefixes=shm.Generator.dutch_prefixes, bind_morphemes=shm.Generator.dutch_bind_morphemes)
count = 0
total = 1
generated_hypotheses = []
for cnt, line in enumerate(open(f_wlist, 'r')):
	d = g.decompound(line.strip())
	if len(d) != 0:
		generated_hypotheses.append(d)
sys.stderr.write('{0}/{1} possible compound(s) found\n'.format(len(generated_hypotheses), cnt))

#TODO: Provide flatten function for debugging

# Select best semantic head hypothesis
