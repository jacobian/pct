import re


def camel_to_spaced(s):
    """
    Convert CamelCasedNames to Names With Spaces.

    See https://stackoverflow.com/a/9283563 for an explanation of that horrific regex.
    I moddified it by adding numbers to the lowercase groups, so e.g. "Hwy20" becomes "Hwy 20"
    """
    pattern = r"""(
                      # Alternative 1:
        (?<=[a-z])    # current position is preceded by a lower char
        [A-Z0-9]      # an upper char or number

        |
                      # Alternative 2:
        (?<!\A)       # current position is not at the beginning of the string
        [A-Z0-9]      # an upper char or number
        (?=[a-z])     # matches if next char is a lower char
    )"""
    return re.sub(pattern, r" \1", s, flags=re.VERBOSE)

