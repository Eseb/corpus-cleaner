#!/usr/bin/env python

import codecs
import re
from argparse import ArgumentParser
from os.path import exists

from corpus_cleaner.shared import DEFAULT_STOP_CHARS, join_regex, ensure_arg


DEFAULT_REORDER_CHARS = ["\"", "'", ")", "]", "}"]
DEFAULT_INPUT_ENCODING = "utf-8"
DEFAULT_OUTPUT_ENCODING = "utf-8"


def remove_excessive_whitespace(text):
    """
    Ensures that there aren't too many linebreaks.
    """
    # limit blank lines to 2
    text = re.sub(r"\n\n+", r"\n\n", text)
    # remove whitespace at the start of the document
    text = re.sub(r"^\s*([^\s])", r"\1", text)
    # remove spaces at the start and end of lines
    text = re.sub(r" *\n *", r"\n", text)
    # limit consecutive spaces to 0
    text = re.sub(r" +", " ", text)
    # remove tabs
    text = text.replace("\t", "")

    return text


def remove_columns(input_text):
    """
    Ensures that text isn't split up into columns arbitrarily. Concatenates what it thinks are
    single sentences into one line.
    """
    paragraphs = re.split("\n\n", input_text)
    solid_paragraphs = []

    for paragraph in paragraphs:
        lines = re.split("\n", paragraph)
        solid_paragraphs.append(" ".join(lines))

    return "\n\n".join(solid_paragraphs)


def reorder_stop_chars(input_text, stop_chars=DEFAULT_STOP_CHARS, reorder_chars=DEFAULT_REORDER_CHARS):
    """
    Fixes problematic orders of stop chars, e.g. American-style quotes where the closing
    quotation mark is outside of the punctuation: "Hello." -> "Hello".
    """
    return re.sub(r"({})({})".format(
        join_regex(stop_chars),
        join_regex(reorder_chars)
    ), r"\2\1", input_text)


def split_as_one_sentence_per_line(input_text, stop_chars=DEFAULT_STOP_CHARS):
    """
    Splits paragraphs into one-sentence-per-line.
    """
    sentence_per_line = re.sub(r"({}) *".format(join_regex(stop_chars)), r"\1\n", input_text)
    # Remove last line break
    return re.sub(r"\n$", "", sentence_per_line)


def scrub(text, stop_chars=DEFAULT_STOP_CHARS, reorder_chars=DEFAULT_REORDER_CHARS):
    """
    Scrub text. Runs the relevant functions in an appropriate order.
    """
    text = reorder_stop_chars(text, stop_chars=stop_chars, reorder_chars=reorder_chars)
    text = remove_columns(text)
    text = split_as_one_sentence_per_line(text, stop_chars=stop_chars)
    text = remove_excessive_whitespace(text)

    return text


def scrub_file(input_path, output_path=None, stop_chars=DEFAULT_STOP_CHARS, reorder_chars=DEFAULT_REORDER_CHARS,
               input_encoding=DEFAULT_INPUT_ENCODING, output_encoding=DEFAULT_OUTPUT_ENCODING):
    """
    Run scrubbing on an entire file's contents. Overwrites if no input is given.
    """
    # Overwrite file if no output path is given
    output_path = output_path if output_path is not None else input_path

    with codecs.open(input_path, "r", input_encoding) as input_file:
        file_contents = input_file.read()

    scrubbed_contents = scrub(file_contents, stop_chars=stop_chars, reorder_chars=reorder_chars)

    with codecs.open(output_path, "w", output_encoding) as output_file:
        output_file.write(scrubbed_contents)

    print("Scrubbed {} to {}".format(input_path, output_path))


def create_arg_parser():
    description = "Tidies up natural language files into one-sentence-per-line easily-parsed files."
    parser = ArgumentParser(description=description)

    parser.add_argument("input", type=unicode,
                        help="Input file to scrub.")
    parser.add_argument("-o, --output", metavar="output-path", type=unicode, dest="output",
                        help="Scrubbed version output path.")

    parser.add_argument("--input-encoding", metavar="encoding", type=unicode, dest="input_encoding",
                        default=DEFAULT_INPUT_ENCODING,
                        help=" ".join([
                            "What encoding to interpret the input files as being.",
                            "Default: {}".format(DEFAULT_INPUT_ENCODING)
                        ]))

    parser.add_argument("--output-encoding", metavar="encoding", type=unicode, dest="output_encoding",
                        default=DEFAULT_OUTPUT_ENCODING,
                        help="What encoding to save the output files as. Default: {}".format(DEFAULT_OUTPUT_ENCODING))

    default_stop_chars = "".join(DEFAULT_STOP_CHARS)
    parser.add_argument("-s, --stop-chars", metavar="stop-chars", dest="stop", type=unicode, default=default_stop_chars,
                        help="Chars defining sentence boundaries. Default: {}".format(default_stop_chars))

    default_reorder_chars = "".join(DEFAULT_REORDER_CHARS)
    parser.add_argument("-r, --reorder", metavar="reorderable", dest="reorder", type=unicode,
                        default=default_reorder_chars,
                        help="Chars which can be swapped with stop chars. Default: {}".format(default_reorder_chars))

    return parser


if __name__ == "__main__":
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    parsed_stop_chars = list(args.stop)
    parsed_reorder_chars = list(args.reorder)

    ensure_arg(exists(args.input), "Input file doesn't exist.", arg_parser)
    ensure_arg(len(parsed_stop_chars) > 0, "Stop characters are invalid", arg_parser)
    ensure_arg(len(parsed_stop_chars) > 0, "Reorderable chars missing.", arg_parser)

    scrub_file(args.input, args.output, stop_chars=parsed_stop_chars, reorder_chars=parsed_reorder_chars,
               input_encoding=args.input_encoding, output_encoding=args.output_encoding)
