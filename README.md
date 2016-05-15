# Corpus cleaner [![Build Status](https://travis-ci.org/Eseb/corpus-cleaner.svg?branch=master)](https://travis-ci.org/Eseb/corpus-cleaner)

A selection of scripts for transforming natural-language corpus files into a clean, consistent format.

# Installation

Python 2.7 or 3.2 is required.

If you have `pip` on your system you can install `corpus-cleaner` through it:

```bash
sudo pip install corpus-cleaner
```

Alternatively, install it manually after cloning:

```bash
git clone https://github.com/Eseb/corpus-cleaner.git
cd corpus-cleaner
sudo python setup.py install
```

After installation, you should be able to use `scrubber.py` & `equaliser.py` from anywhere in your shell.

If you want to incorporate these scripts into your existing Python workflow, they provide easy-to-use entry functions you can use.

# Scrubber

`scrubber.py` fixes common corpus issues and outputs files in a common format: one sentence per line, and paragraphs are separated by a blank line.

Some helpful things `scrubber` does:

- Removes excessive whitespace
- Rearranges files with arbitrary columns
- Swaps sentence-boundary-characters with wrap-closing characters (e.g. `"Hi."` -> `"Hi".`)
- Re-encodes files to your desired codec

```
This file is split into arbitrary-length
columns for no good reason. While you
could go through it by hand trying to
fix it, it's much easier to just use
this script to automate the process.



Woah, do you see how many linebreaks there
 are between these paragraphs? Wait, was
that a space at the start of that line!?
```

**Becomes**

```
This file is split into arbitrary-length columns for no good reason.
While you could go through it by hand trying to fix it, it's much easier to just use this script to automate the process.

Woah, do you see how many linebreaks there are between these paragraphs?
Wait, was that a space at the start of that line!?
```

# Equaliser

`equaliser.py` attempts to make two parallel SMT corpuses of equal sentence-length. It assumes that each paragraph maps to the one in the other file, and it merges sentences into parallel ones of similar length in an attempt to capture the same meaning in parallel sentences.

Any sentences or paragraphs that cannot be mapped to another will be discarded.

| E | F |
| --- | --- |
| I should be left alone. | I should also be left alone. |
| I should get merged. | I am really damn long, so I should force a merge. |
| With this one. | I shouldn't force a merge in the other paragraph. |
| I should not be merged. | The three of us. |
| Because this one is so long, merging me with the previous one is a bad idea. | Myself included, remember! |
| | Will all get merged together. |
| | I will be dropped. |

**Becomes**

| E | F |
| --- | --- |
| I should be left alone. | I should also be left alone. |
| I should get merged with this one. | I am really damn long, so I should force a merge. |
| I should not be merged. | I shouldn't force a merge in the other paragraph. |
| Because this one is so long, merging me with the previous one is a bad idea. | The three of us myself included, remember will all get merged together. |
