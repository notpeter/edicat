from io import BufferedReader, BytesIO

from typing import Dict, Iterator, Union, BinaryIO


def readdocument(edi: Union[str, BinaryIO]) -> Iterator[str]:
    """Splits text on a line_break character (unless preceeded by an escape character)."""
    if isinstance(edi, str):
        sep = detect(edi)
        edi = BytesIO(edi.encode('utf-8'))
    else:
        edi = BufferedReader(edi)
        sep = detect(str(edi.peek(110), 'ascii'))

    line_break = bytes(sep['segment'], 'ascii')
    escape = bytes(sep['escape'], 'ascii') if 'escape' in sep else None
    character = ''
    buf = []

    while True:
        last = character  # previously read character
        character = edi.read(1)  # EOF returns b''
        buf.append(str(character, 'utf-8'))
        if (character == line_break and last != escape) or character == b'':
            line = "".join(buf).strip()
            buf[:] = []
            if line:
                yield line
            if character == b'':
                break


def detect(text: str) -> Dict[str, str]:
    # EDI X12: begins with ISA (106 chars) followed by a GS segment
    sep = {}
    if text.startswith('ISA') and 'GS' in text[106:110]:
        sep = {'element': text[103],
               'subelement': text[104],
               'segment': text[105],
               'suffix': text[106:text.find('GS')]}
        if text[82] != 'U':  # X12 before repetition has 'U' here.
            sep['repetition'] = text[82]
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
        # TODO: warning not error
        raise NotImplementedError("Unknown EDI format.")
    return sep
