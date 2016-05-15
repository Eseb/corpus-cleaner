#!/usr/bin/env python

from distutils.core import setup

setup(name="corpus-cleaner",
      version="0.1.0",
      description="Natural-language corpus cleaning scripts",
      author="Seb Bacanu",
      keywords=["smt", "nlp", "corpus"],
      author_email="seb@bacanu.com",
      url="https://github.com/Eseb/corpus-cleaner",
      download_url="https://github.com/Eseb/corpus-cleaner/tarball/v0.1.0",
      packages=["corpus_cleaner"],
      scripts=['corpus_cleaner/scrubber.py', 'corpus_cleaner/equaliser.py'])
