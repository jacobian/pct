import pytest
from pct.junkdrawer import camel_to_spaced


@pytest.mark.parametrize(
    "input,expected",
    [
        # Most things work ok
        ("HartsPass", "Harts Pass"),
        ("Hwy20", "Hwy 20"),
        ("BoulderOakCG", "Boulder Oak CG"),
        ("CreekFCTr", "Creek FC Tr"),

        # A few things aren't perfect but w/e
        ("WACS016", "WACS016"),
        ("RD0001B", "RD0001B"),
        ("BlackMtnGC-BMR", "Black Mtn GC-BMR"),
    ],
)
def test_camel_to_spaced(input, expected):
    assert camel_to_spaced(input) == expected
