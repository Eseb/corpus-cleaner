#!/usr/bin/env python

import re
from argparse import ArgumentParser
from os.path import exists, basename

from corpus_cleaner.shared import DEFAULT_STOP_CHARS, join_regex, ensure_arg

DEFAULT_SENTENCE_RATIO = 0.6
DEFAULT_LOWERCASE_GLUED = True

A_IS_LONGER = -1
BOTH_EQUIVALENT = 0
B_IS_LONGER = 1


def split(text):
    """
    Splits text into a list of paragraphs, each of which is a list of sentences.
    """
    paragraphs = text.split("\n\n")
    paragraphs = [paragraph.split("\n") for paragraph in paragraphs]

    return paragraphs


def merge(paragraphs):
    """
    Merges the list-inside-list paragraph format back into one string
    """
    paragraphs = ["\n".join(sentences) for sentences in paragraphs]
    return "\n\n".join(filter(lambda paragraph: len(paragraph) != 0, paragraphs))


def compare_sentences(sentence_a, sentence_b, sentence_ratio=DEFAULT_SENTENCE_RATIO):
    """
    Returns (A_IS_HIGHER | SENTENCES_EQUIVALENT | B_IS_HIGHER) while keeping into account sentence ratio.
    """
    a_word_count = len(sentence_a.split(" "))
    b_word_count = len(sentence_b.split(" "))

    a_higher = a_word_count * sentence_ratio > b_word_count
    b_higher = b_word_count * sentence_ratio > a_word_count

    if not (a_higher or b_higher):
        return BOTH_EQUIVALENT

    return A_IS_LONGER if a_higher else B_IS_LONGER


def glue_sentences(first, second, lowercase_glued=DEFAULT_LOWERCASE_GLUED, stop_chars=DEFAULT_STOP_CHARS):
    """
    Attached two sentences together, removing punctuation
    """
    if lowercase_glued and len(second) != 0:
        second = second[0].lower() + second[1:]

    # Remove stop-char from the first sentence
    first = re.sub(r"({})$".format(join_regex(stop_chars)), "", first)

    return "{} {}".format(first, second)


def equalise_paragraphs(a_para, b_para, sentence_ratio=DEFAULT_SENTENCE_RATIO, lowercase_glued=DEFAULT_LOWERCASE_GLUED,
                        stop_chars=DEFAULT_STOP_CHARS):
    """
    Glues together two collections of sentences so that they're of similar
    word-length. Discards sentences it cannot make parallel.
    """
    equalised_a_para = []
    equalised_b_para = []

    a_index = 0
    b_index = 0

    # Keep merging while we still have sentences to draw from
    while a_index < len(a_para) and b_index < len(b_para):
        a_sentence = a_para[a_index]
        b_sentence = b_para[b_index]

        comparison_result = compare_sentences(a_sentence, b_sentence, sentence_ratio=sentence_ratio)

        try:
            if comparison_result == B_IS_LONGER:
                next_a_sentence = a_para[a_index + 1]
                glued = glue_sentences(a_sentence, next_a_sentence,
                                       lowercase_glued=lowercase_glued, stop_chars=stop_chars)

                if compare_sentences(glued, b_sentence, sentence_ratio=sentence_ratio) != A_IS_LONGER:
                    # Expand the next sentence and move the index to it for the next pass
                    a_para[a_index + 1] = glued
                    a_index += 1
                else:
                    # Force a push
                    comparison_result = BOTH_EQUIVALENT
            elif comparison_result == A_IS_LONGER:
                next_sentence = b_para[b_index + 1]
                glued = glue_sentences(b_sentence, next_sentence,
                                       lowercase_glued=lowercase_glued, stop_chars=stop_chars)

                if compare_sentences(a_sentence, glued, sentence_ratio=sentence_ratio) != B_IS_LONGER:
                    # Expand the next sentence and move the index to it for the next pass
                    b_para[b_index + 1] = glued
                    b_index += 1
                else:
                    # Force a push
                    comparison_result = BOTH_EQUIVALENT

            if comparison_result == BOTH_EQUIVALENT:
                # Sentences are close enough to being equal. Keep going.
                equalised_a_para.append(a_sentence)
                equalised_b_para.append(b_sentence)
                a_index += 1
                b_index += 1
        except IndexError:
            # Hit if we try to access any next_sentence that doesn't exist. We're done if that happens.
            break

    return equalised_a_para, equalised_b_para


def equalise(text_a, text_b, sentence_ratio=DEFAULT_SENTENCE_RATIO, lowercase_glued=DEFAULT_LOWERCASE_GLUED,
             stop_chars=DEFAULT_STOP_CHARS):
    """
    Assuming that paragraphs are equivalent, compact the 2 texts into
    equal-paragraph-count and equal-sentence-count versions of themselves.
    """
    a_paragraphs = split(text_a)
    b_paragraphs = split(text_b)

    equalised_a_paragraphs = []
    equalised_b_paragraphs = []

    fewest_paragraph_count = min(len(a_paragraphs), len(b_paragraphs))

    for paragraph_index in range(0, fewest_paragraph_count):
        a_para = a_paragraphs[paragraph_index]
        b_para = b_paragraphs[paragraph_index]

        equalised_a_para, equalised_b_para = equalise_paragraphs(a_para, b_para, sentence_ratio=sentence_ratio,
                                                                 lowercase_glued=lowercase_glued, stop_chars=stop_chars)
        equalised_a_paragraphs.append(equalised_a_para)
        equalised_b_paragraphs.append(equalised_b_para)

    return equalised_a_paragraphs, equalised_b_paragraphs


def equalise_file(file_a, file_b, sentence_ratio=DEFAULT_SENTENCE_RATIO, lowercase_glued=DEFAULT_LOWERCASE_GLUED,
                  stop_chars=DEFAULT_STOP_CHARS):
    """
    Performs equalisation process on two files.
    """
    with open(file_a, "r") as input_file:
        file_a_contents = input_file.read()
    with open(file_b, "r") as input_file:
        file_b_contents = input_file.read()

    original_corpus_size = (len(file_a_contents) + len(file_b_contents)) / 2

    equalised_a, equalised_b = equalise(file_a_contents, file_b_contents, sentence_ratio=sentence_ratio,
                                        lowercase_glued=lowercase_glued, stop_chars=stop_chars)

    equalised_a = merge(equalised_a)
    equalised_b = merge(equalised_b)

    with open(file_a, "w") as output_file:
        output_file.write(equalised_a)
    with open(file_b, "w") as output_file:
        output_file.write(equalised_b)

    equalised_corpus_size = (len(equalised_a) + len(equalised_b)) / 2
    corpus_lost = int((1.0 - float(equalised_corpus_size) / original_corpus_size) * 100)

    print("Scrubbed {} & {}. Corpus lost: {}%".format(basename(file_a), basename(file_b), corpus_lost))


def create_arg_parser():
    description = "Makes two corpus files of equal-sentence-length by merging sentences where it thinks appropriate."
    parser = ArgumentParser(description=description)

    parser.add_argument("file_a", type=unicode,
                        help="Input file A. Order is irrelevant.")
    parser.add_argument("file_b", type=unicode,
                        help="Input file B. Order is irrelevant.")

    parser.add_argument("-r, --ratio", dest="ratio", type=float, default=DEFAULT_SENTENCE_RATIO,
                        help=" ".join([
                            "How close in word-count sentences have to be to be considered equivalent as a 0 to 1 ratio",
                            "Default: {}".format(DEFAULT_SENTENCE_RATIO)
                        ]))

    default_stop_chars = "".join(DEFAULT_STOP_CHARS)
    parser.add_argument("-s, --stop-chars", dest="stop", metavar="stop-chars", type=unicode, default=default_stop_chars,
                        help="Chars defining sentence boundaries. Default: {}".format(default_stop_chars))

    parser.add_argument("-k, --keep-case", dest="keep_case", default=False,
                        action="store_true", help="Don't lowercase the first char of the second sentence in a merge.")

    return parser


if __name__ == "__main__":
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    user_stop_chars = list(args.stop)
    user_lowercase_glued = not args.keep_case

    ensure_arg(exists(args.file_a), "File A doesn't exist.", arg_parser)
    ensure_arg(exists(args.file_b), "File B doesn't exist.", arg_parser)
    ensure_arg(len(user_stop_chars) != 0, "Stop characters are invalid.", arg_parser)

    equalise_file(args.file_a, args.file_b, sentence_ratio=args.ratio, stop_chars=user_stop_chars,
                  lowercase_glued=user_lowercase_glued)
