from unittest import TestCase, main
import re
import scrub


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
            scrub.remove_excessive_whitespace(prepare_test_string("""


                This line should not have any linebreaks above it, and only two below it.



                   \tThere should be no spaces or tabs in front or at the end of this line.
                There  should   only be    one space     between   words.
            """))
        )

    def test_remove_columns(self):
        self.assertEqual(
            prepare_test_string("""
                One morning, when Gregor woke from troubled dreams, he found himself transformed into a horrible vermin.

                He lay on his armour-like back, and if he lifted his head a little he could see his brown belly.
            """),
            scrub.remove_columns(prepare_test_string("""
                One morning, when Gregor woke from troubled dreams,
                he found himself transformed into a horrible vermin.

                He lay on his armour-like back,
                and if he lifted his head a little he could see his brown belly.
            """))
        )

    def test_reorder_stop_chars(self):
        self.assertEqual(
            "Gregor found himself transformed into a \"horrible vermin\".",
            scrub.reorder_stop_chars("Gregor found himself transformed into a \"horrible vermin.\"")
        )

    def test_split_paragraphs(self):
        self.assertEqual(
            prepare_test_string("""
                One morning, when Gregor woke from troubled dreams, he found himself transformed into a vermin.
                He lay on his armour-like back, and if he lifted his head a little he could see his brown belly.
            """),
            # One-line
            scrub.split_as_one_sentence_per_line(
                "One morning, when Gregor woke from troubled dreams, he found himself transformed into a vermin." +
                "He lay on his armour-like back, and if he lifted his head a little he could see his brown belly."
            )
        )


if __name__ == "__main__":
    main()
