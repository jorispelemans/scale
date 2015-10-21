#! /usr/bin/env python

import sys, math
from collections import defaultdict

if (len(sys.argv) < 3):
	sys.stderr.write('Usage: score_decomp(_full).py <decompounding-file> <ground-truth-file>\n\n')
	sys.stderr.write('Counts the number of tp, fp, tn, fn and fp_only (see last lines of script source for info on this) decompoundings in the given file, based on the given ground truth. The ground truth file should be in the format of "modifiers head"\n')
else:
	MODE = 'NORMAL'
	if sys.argv[0].endswith('score_paper.py'):
		MODE = 'FULL'
	f_decomp = sys.argv[1]
	f_gt = sys.argv[2]
#	settings = ''
#	if len(sys.argv) > 3:
#		settings = sys.argv[3]
	if len(sys.argv) > 3:
		DEBUG = True
	else:
		DEBUG = False

	decomp = defaultdict(set)
	if f_decomp.endswith('.vdg') or f_decomp.endswith('.best') or f_decomp.endswith('.tmp'):
		for line in open(f_decomp,'r'):
			l = line.strip().split('=')
			w = l[0].strip()
			d = l[1].strip()
			h = d.split()
			if len(h) > 1:
				decomp[w].add(h[-1])
#				sys.stderr.write('{0}\n'.format(h))

	else:
		for line in open(f_decomp,'r'):
			l = line.strip().split('=')
			w = l[0].replace('*','').strip()
			d = l[1].split('+')
			if len(d) > 1:
				h = d[-1].replace('(LEX)','').strip()
#				sys.stderr.write('{0}\n'.format(h))
				decomp[w].add(h)

	#gt = {}	
	gt = defaultdict(set) # multiple (unique) solutions
	total = 0.0
	for line in open(f_gt,'r'):
		total += 1
		l = line.strip().split()
		if len(l) > 1:
			#gt[''.join(l)] = l[1]
			gt[''.join(l)].add(l[1]) # multiple unique solutions
		else:
#			gt[''.join(l)] = ''
			gt[''.join(l)] = set()

	#for w in gt:
	#	print '{0} = {1}'.format(w,gt[w])

	#for w in decomp:
	#	print '{0} = {1}'.format(w,decomp[w])

	count_tp = 0
	count_fp = 0
	count_fp_only = 0
	count_fn = 0
	count_tn = 0
	uniq_fp = 0
	uniq_fp_only = 0
	if DEBUG:
		fn = open(f_decomp + '.fn','wa')
		tn = open(f_decomp + '.tn','wa')
		fp = open(f_decomp + '.fp','wa')
		fp_only = open(f_decomp + '.fp_only','wa')
		tp = open(f_decomp + '.tp','wa')
	for w in gt:
		d = decomp[w]
		# negative: no decompounding found
		if len(d) == 0:
			# true negative: correctly found no decompounding
			#if gt[w]=='':
			if len(gt[w]) == 0:
				count_tn += 1
				if DEBUG:
					tn.write('{0}\n'.format(w))
			# false negative: missed a decompounding
			else:
				count_fn += 1
				if DEBUG:
					fn.write('{0}\n'.format(w))
		# positive: decompounding(s) found
		else:
			bool_fp_only = False
#			if gt[w] not in d:
#				bool_fp_only = True
			if len(gt[w]) == 0:
				bool_fp_only = True
			else:
				for g in gt[w]: # multiple solutions
					if g not in d:
						bool_fp_only = True
			found_fp = False
			for h in d:
				# true positive: correct decompounding found
				#if h == gt[w]:
				if h in gt[w]: # multiple solutions
					count_tp += 1
					if DEBUG:
						tp.write('{0} = {1}\n'.format(w,h))
				# false positive: incorrect decompounding found
				else:
					if not found_fp:
						uniq_fp += 1
					count_fp += 1
					if DEBUG:
						fp.write('{0} = {1}\n'.format(w,h))
					if bool_fp_only:
						if not found_fp:
							uniq_fp_only += 1
						count_fp_only += 1
						if DEBUG:
							fp_only.write('{0} = {1}\n'.format(w,h))
					found_fp = True

	if DEBUG:
		fn.close()
		fp.close()
		fp_only.close()
		tn.close()
		tp.close()
	if MODE == 'NORMAL':
		try:
			ratio = float(count_tp) / count_fp_only
		except ZeroDivisionError:
			sys.stderr.write('\nWARNING: No fp_only? Either your system is EXTREMELY good or you did not give your file the extension .best\n')
		print 'tp = {0} -- found correct decompounding'.format(count_tp)
		print 'fp = {0} -- found incorrect decompounding'.format(count_fp)
		print 'tn = {0} -- correctly found no decompounding'.format(count_tn)
		print 'fn = {0} -- missed a decompounding'.format(count_fn)
		print 'fp_only = {0} -- found only incorrect decompounding'.format(count_fp_only)
		print 'tp/fp_only = {0:.2f}'.format(ratio)
	elif MODE == 'FULL':
		#if uniq_fp_only == 0 or fp_only == 0:
		if uniq_fp_only == 0 or count_fp_only == 0:
			sys.stderr.write('\nWARNING: No (uniq_)fp_only? Either your system is EXTREMELY good or you did not give your file the extension .best\n')
		try:
			ratio = float(count_tp) / uniq_fp_only
		except ZeroDivisionError:
			ratio = 0
		tpp = float(count_tp) / len(gt) * 100
		fpp = float(count_fp) / len(gt) * 100
		tnp = float(count_tn) / len(gt) * 100
		fnp = float(count_fn) / len(gt) * 100
		fp_onlyp = float(count_fp_only) / len(gt) * 100
		ufpp = float(uniq_fp) / len(gt) * 100
		ufp_onlyp = float(uniq_fp_only) / len(gt) * 100
		try:
			avg_fp = float(count_fp) / uniq_fp
		except ZeroDivisionError:
			avg_fp = 0
		try:
			avg_fp_only = float(count_fp_only) / uniq_fp_only
		except ZeroDivisionError:
			avg_fp_only = 0
#		print '{0:^9}|{1:^9}|{2:^9}|{3:^9}|{4:^10}|{5:^7}|{6:^7}|{7:^7}|{8:^7}|{9:^11}|{10:^8}|{11:^13}|{12:^13}'.format('tp','ufp','tn','fn','ufp_only','tp%','ufp%','tn%','fn%','ufp_o%','avg_fp','avg_fp_o','tp/ufp_o')
#		print settings,
#		print '{0:^9}|{1:^9}|{2:^9}|{3:^9}|{4:^10}|{5:^7.2f}|{6:^7.2f}|{7:^7.2f}|{8:^7.2f}|{9:^8.2f}|{10:^8.2f}|{11:^10.2f}|{12:^10.2f}'.format(count_tp,uniq_fp,count_tn,count_fn,uniq_fp_only,tpp,ufpp,tnp,fnp,ufp_onlyp,avg_fp,avg_fp_only,ratio)
		precision = float(count_tp)/(count_tp+count_fp)*100
		recall = float(count_tp)/(count_tp+count_fn)*100
		sys.stderr.write('Precision = {0}\n'.format(precision))
		sys.stderr.write('Recall = {0}\n'.format(recall))
		for beta in [0.05, 0.1, 0.2, 0.25, 0.5, 0.75]:
			F_beta = (1 + math.pow(beta,2)) * precision * recall / ((math.pow(beta,2) * precision) + recall)
			sys.stdout.write('{0}\t'.format(F_beta))
			sys.stderr.write('F_{0} = {1}\n'.format(beta,F_beta))
		print
