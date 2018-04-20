import sys
from io import BufferedReader, BytesIO
from typing import Dict, Iterator, Union, BinaryIO


# ISA has fixed width elements. These should all be equal. 103 is official sep.element position
isa_element_sep = [3, 6, 17, 20, 31, 34, 50, 53, 69, 76, 81, 83, 89, 99, 101, 103]
isa_example = "ISA*00*          *00*          *ZZ*SOMEBODYELSE   *ZZ*MAYBEYOU       *171231*2359*U*00401*000012345*0*P*:~"  # noqa


def readdocument(edi: Union[str, BinaryIO], filename='stream') -> Iterator[str]:
    """Splits text on a line_break character (unless preceeded by an escape character)."""
    if isinstance(edi, str):
        sep = detect(edi)
        edi = BytesIO(edi.encode('utf-8'))
    else:
        edi = BufferedReader(edi)
        sep = detect(str(edi.peek(110), 'ascii'))
    if not sep:
        print("Skipping...%s" % filename, file=sys.stderr)
        return

    line_break = bytes(sep['segment'], 'ascii')
    escape = bytes(sep['escape'], 'ascii') if 'escape' in sep else None
    blacklist = {b'\r', b'\n'} if sep.get('hard_wrap') else set()
    last = ''
    character = ''
    buf = []

    while True:
        character = edi.read(1)  # EOF returns b''
        if character in blacklist:
            continue
        buf.append(str(character, 'utf-8'))
        if (character == line_break and last != escape) or character == b'':
            line = "".join(buf).strip()
            buf[:] = []
            if line:
                yield line
            if character == b'':
                break
        last = character  # previously read character


def detect(text: str) -> Dict[str, str]:
    """Takes an EDI string and returns detected separators as a dictionary."""

    sep = {}
    # EDI X12: begins with ISA (106 chars) followed by a GS segment
    if text.startswith('ISA'):
        if 'GS' in text[106:110] and len(set([text[pos] for pos in isa_element_sep])) == 1:
            sep = {'element': text[103],
                   'subelement': text[104],
                   'segment': text[105],
                   'suffix': text[106:text.find('GS')]}
            if text[82] != 'U':  # X12 before repetition has 'U' here.
                sep['repetition'] = text[82]
        else:
            print("Invalid X12 ISA Header.",
                  "Expected: %s" % isa_example,
                  "Received: '%r'" % (text[:106]),
                  file=sys.stderr, sep="\n")
    # Edifact UNA: begins with UNA followed by UNB or UNG
    elif text.startswith('UNA') and 'UN' in text[3:13]:
        # ex: """UNA:+.? '\r\nUN..."""
        sep = {'subelement': text[3],
               'element': text[4],
               'release': text[6],
               'segment': text[8],
               'suffix': text[9:text.find('UN')]}
        if text[7] != ' ':  # Edifact before repetition has ' ' here.
            sep['repetition'] = text[7]
    # Edifact no UNA: begins with UNB followed by UNH
    elif text.startswith('UNB') and 'UN' in text[3:13]:
        sep = {'subelement': ':',
               'element': '+',
               'segment': "'",
               'release': '?',
               'repetition': '*',
               'suffix': text[text.find("'") + 1:text.find('UN', 3)]}
    else:
        print("Found something that doesn't look like EDI: %r" % text[:8], file=sys.stderr)

    # This detects "hard wrapped" EDI files where a CRLF is inserted every 80 chars
    # TODO: Potentially support LF (\n) only hard wrap.
    if (text[80] == text[162] == text[244] == '\r' and
        text[81] == text[163] == text[245] == '\n'):
        sep['hard_wrap'] = True
    return sep
