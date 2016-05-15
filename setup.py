#!/usr/bin/env python

from distutils.core import setup

setup(name="corpus_cleaner",
      version="0.1.0",
      description="Natural-language corpus cleaning scripts",
      author="Seb Bacanu",
      author_email="seb@bacanu.com",
      url="https://github.com/Eseb/corpus-cleaner",
      packages=["corpus_cleaner"],
      scripts=['corpus_cleaner/scrubber.py', 'corpus_cleaner/equaliser.py'])
