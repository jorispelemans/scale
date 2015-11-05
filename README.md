# SCALE -- A Scalable Language Engineering Toolkit

SCALE is a Python toolkit that contains two extensions to n-gram Language Models: Semantic Head Mapping (SHM) and Bag-of-Words Language Modeling (BagLM). Both of them scale to large data and allow the integration into first-pass ASR decoding. More information about these extensions can be found in the following papers:

* Joris Pelemans, Kris Demuynck, Hugo Van hamme and Patrick Wambacq. Coping with Language Data Sparsity: Semantic Head Mapping for Compound Words. In Proc. ICASSP, Firenze, Italy, May 2014. 
* Joris Pelemans, Kris Demuynck, Hugo Van hamme and Patrick Wambacq. Improving N-gram Probabilities by Compound-head Clustering. In Proc. ICASSP, Brisbane, Australia, April 2015. 
* Joris Pelemans, Kris Demuynck, Hugo Van hamme and Patrick Wambacq. The effect of word similarity on N-gram language models in Northern and Southern Dutch. Computational Linguistics in the Netherlands, volume 24, February 2015. 

The toolkit is open source, includes working examples and can be found on http://github.com/jorispelemans/scale. It is still quite new, so we're actively working on providing more documentation. If you encounter any bugs, please report and we will fix them asap.

## Installation

SCALE depends on [gensim] (http://radimrehurek.com/gensim) which is most efficient if you have also installed [Cython] (http://cython.org/). The easiest way to install gensim is:
```
pip install -U setuptools
pip install -U Cython gensim
```

To install SCALE, run:
```
python setup.py install
```
