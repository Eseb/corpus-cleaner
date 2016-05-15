from unittest import TestCase, main
import re

from corpus_cleaner import scrubber, equaliser


def prepare_test_string(string):
    """
    Removes the line-breaks at the start and end of the test strings, as well as tabs
    """
    # Remove tab-spaces in multiples of 4 only
    string = re.sub(r"(^|\n)( {4}|\t)+", r"\1", string)
    string = re.sub(r"(^\n)|(\n$)", "", string)

    return string


class ScrubTest(TestCase):

    def test_remove_excessive_whitespace(self):
        self.assertEqual(
            prepare_test_string("""
                This line should not have any linebreaks above it, and only two below it.

                There should be no spaces or tabs in front or at the end of this line.
                There should only be one space between words.
            """),
            scrubber.remove_excessive_whitespace(prepare_test_string("""


                This line should not have any linebreaks above it, and only two below it.



                   \tThere should be no spaces or tabs in front or at the end of this line.
                There  should   only be    one space     between   words.
            """))
        )

    def test_remove_columns(self):
        self.assertEqual(
            "This paragraph is split up into columns for no good reason.",
            scrubber.remove_columns(prepare_test_string("""
                This paragraph is
                split up into columns
                for no good reason.
            """))
        )

    def test_reorder_stop_chars(self):
        self.assertEqual(
            "American English calls full stops 'periods'; they also insert them before closing \"quotation marks\"!",
            scrubber.reorder_stop_chars(
                "American English calls full stops 'periods;' they also insert them before closing \"quotation marks!\""
            )
        )

    def test_split_as_one_sentence_per_line(self):
        self.assertEqual(
            prepare_test_string("""
                This is the first sentence in this paragraph.
                This is the second--should be on its own line.
            """),
            # One-line
            scrubber.split_as_one_sentence_per_line(prepare_test_string("""
                This is the first sentence in this paragraph. This is the second--should be on its own line.
            """))
        )


class EqualiserTest(TestCase):

    def test_split(self):
        self.assertEqual(
            [
                ["P1S1.", "P1S2."],
                ["P2S1.", "P2S2.", "P2S3."]
            ],
            equaliser.split(prepare_test_string("""
                P1S1.
                P1S2.

                P2S1.
                P2S2.
                P2S3.
            """))
        )

    def test_compare_sentences(self):
        self.assertEqual(
            equaliser.BOTH_EQUIVALENT,
            equaliser.compare_sentences(
                "these sentences are pretty much equivalent",
                "these sentences are actually equivalent"
            )
        )

        self.assertEqual(
            equaliser.A_IS_LONGER,
            equaliser.compare_sentences(
                "this sentence is longer than the second one",
                "i am short"
            )
        )

        self.assertEqual(
            equaliser.B_IS_LONGER,
            equaliser.compare_sentences(
                "now i am short",
                "i am long enough to beat you this time"
            )
        )

    def test_glue_sentences(self):
        self.assertEqual(
            "I like apples i am lowercase.",
            equaliser.glue_sentences(
                "I like apples.",
                "I am lowercase.",
                lowercase_glued=True
            )
        )

        self.assertEqual(
            "I like apples I am uppercase.",
            equaliser.glue_sentences(
                "I like apples.",
                "I am uppercase.",
                lowercase_glued=False
            )
        )

    def test_equalise_paragraphs(self):
        a_result, b_result = equaliser.equalise_paragraphs([
            "I should be left alone.", "I should get merged.", "with this one.", "I should not be merged",
            "Because this one is so long, merging me with the previous one is a bad idea."
        ], [
            "I should also be left alone.", "I am really damn long, so I should force a merge.",
            "I shouldn't force a merge in the other paragraph.",
            "The three of us.", "Myself included, remember!", "Will all get merged together.",
            "I will be dropped."
        ])

        a_expected = [
            "I should be left alone.", "I should get merged with this one.",
            "I should not be merged", "Because this one is so long, merging me with the previous one is a bad idea."
        ]

        b_expected = [
            "I should also be left alone.", "I am really damn long, so I should force a merge.",
            "I shouldn't force a merge in the other paragraph.",
            "The three of us myself included, remember will all get merged together."
        ]

        self.assertEqual((a_expected, b_expected), (a_result, b_result))
        # The whole point is to have equal sentence counts
        self.assertEqual(len(a_result), len(b_result))


if __name__ == "__main__":
    main()
