# Corpus cleaner

A selection of scripts for transforming natural-language corpus files into a clean, consistent format.

# Scrubber

`scrubber.py` fixes common corpus issues and outputs files in a common format: one sentence per line, and paragraphs are separated by a blank line.

Some helpful things `scrubber` does:

- Removes excessive whitespace
- Rearranges files with arbitrary columns
- Swaps sentence-boundary-characters with wrap-closing characters (e.g. `"Hi."` -> `"Hi".`)
- Re-encodes files to your desired codec

## Scrubber example

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
Becomes
```
This file is split into arbitrary-length columns for no good reason.
While you could go through it by hand trying to fix it, it's much easier to just use this script to automate the process.

Woah, do you see how many linebreaks there are between these paragraphs?
Wait, was that a space at the start of that line!?
```

# Equaliser

`equaliser.py` attempts to make two parallel SMT corpuses of equal sentence-length. It assumes that each paragraph maps to the one in the other file, and it merges sentences into parallel ones of similar length in an attempt to capture the same meaning in parallel sentences.

Any sentences or paragraphs that cannot be mapped to another will be discarded.
