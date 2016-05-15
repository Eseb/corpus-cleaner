import re

DEFAULT_STOP_CHARS = [".", ";", "!", "?"]


def join_regex(target_list):
    """
    Takes a list of chars and joins then into a regex-friendly search string
    """
    return "|".join([re.escape(item) for item in target_list])


def ensure_arg(condition_met, failure_message, parser):
    """
    Make sure that the given arg is valid
    """
    if condition_met:
        return

    print(failure_message)
    parser.print_usage()
    exit()
