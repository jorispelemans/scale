import sys
import urllib

def download_file(url, fname, progress=False):
	if not progress:
		urllib.urlretrieve(url, fname)
	else:
		global msg
		msg = "Downloading {0}".format(fname)

		def dl_progress(count, block_size, total_size):
			percent = int(count * block_size * 100 / total_size)
			sys.stdout.write("\r{0} ... {1}%".format(msg, percent))
			sys.stdout.flush()
		urllib.urlretrieve(url, fname, dl_progress)

		msg = None
