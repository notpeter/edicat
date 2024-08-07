import sys
from io import BufferedReader, BytesIO
from typing import Iterator, Union

from typing import Optional
from dataclasses import dataclass


@dataclass
class Sep:
    element: str
    segment: str
    subelement: str
    suffix: str
    release: Optional[str] = None
    escape: Optional[str] = None
    repetition: Optional[str] = None
    hard_wrap: bool = False


# ISA has fixed width elements. These should all be equal. 103 is official sep.element position
isa_element_sep = [3, 6, 17, 20, 31, 34, 50, 53, 69, 76, 81, 83, 89, 99, 101, 103]
isa_example = "ISA*00*          *00*          *ZZ*SOMEBODYELSE   *ZZ*MAYBEYOU       *171231*2359*U*00401*000012345*0*P*:~"  # noqa


def readdocument(
    edi_obj: Union[str, BufferedReader], filename: str = "stream", encoding: str = "latin-1"
) -> Iterator[str]:
    """Splits text on a line_break character (unless preceeded by an escape character)."""

    if isinstance(edi_obj, str):
        sep = detect(edi_obj)
        edi = BytesIO(edi_obj.encode(encoding))
    elif isinstance(edi_obj, BufferedReader):
        edi = edi_obj
        sep = detect(str(edi_obj.peek(), encoding))
    else:
        raise ValueError("Expected str or BufferedReader, got %s" % type(edi_obj))

    if sep is None:
        print("Skipping...%s" % filename, file=sys.stderr)
        return

    line_break = bytes(sep.segment, "ascii")
    escape = bytes(sep.escape, "ascii") if sep.escape else None
    blacklist = {b"\r", b"\n"} if sep.hard_wrap else set()
    last = ""
    buf = []

    while True:
        character = edi.read(1)  # EOF returns b''
        if character in blacklist:
            continue
        buf.append(str(character, encoding))
        if (character == line_break and last != escape) or character == b"":
            line = "".join(buf).strip()
            buf[:] = []
            if line:
                yield line
            if character == b"":
                break
        last = character  # previously read character


def detect(text: str) -> Optional[Sep]:
    """Takes an EDI string and returns detected separators as a dictionary."""

    sep: Optional[Sep] = None
    # EDI X12: begins with ISA (106 chars) followed by a GS segment
    if text.startswith("ISA"):
        if "GS" in text[106:110] and len(set([text[pos] for pos in isa_element_sep])) == 1:
            sep = Sep(
                element=text[103],
                subelement=text[104],
                segment=text[105],
                suffix=text[106 : text.find("GS")],
                # X12 before repetition has 'U' here.
                repetition=text[82] if text[82] != "U" else None,
            )
        else:
            print(
                "Invalid X12 ISA Header (expected 16 fixed width fields, 106 characters wide)",
                "Expected: %s" % isa_example,
                "Received: %s" % (text[:106]),
                file=sys.stderr,
                sep="\n",
            )
    # Edifact UNA: begins with UNA followed by UNB or UNG
    elif text.startswith("UNA") and "UN" in text[3:13]:
        # ex: """UNA:+.? '\r\nUN..."""
        sep = Sep(
            subelement=text[3],
            element=text[4],
            release=text[6],
            segment=text[8],
            suffix=text[9 : text.find("UN")],
            # Edifact before repetition has ' ' here.
            repetition=text[7] if text[7] != " " else None,
        )
    # Edifact no UNA: begins with UNB followed by UNH
    elif text.startswith("UNB") and "UN" in text[3:13]:
        sep = Sep(
            subelement=":",
            element="+",
            segment="'",
            release="?",
            repetition="*",
            suffix=text[text.find("'") + 1 : text.find("UN", 3)],
        )

    if sep is None:
        print("Found something that doesn't look like EDI: %r" % text[:8], file=sys.stderr)
    else:
        # This detects "hard wrapped" EDI files where a CRLF is inserted every 80 chars
        # TODO: Potentially support LF (\n) only hard wrap.
        if (
            len(text) > 246
            and text[80] == text[162] == text[244] == "\r"
            and text[81] == text[163] == text[245] == "\n"
        ):
            sep.hard_wrap = True

    return sep
