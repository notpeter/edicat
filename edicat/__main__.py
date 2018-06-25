import argparse
import os
import sys
from typing import BinaryIO, Iterable, Iterator, Tuple

import edicat
from edicat.edi import readdocument


def lprint(line: str, lineno: int, line_numbers: bool = False) -> None:
    """Print a line with optional line number"""
    if line_numbers:
        print("{0: >6}\t{1}".format(lineno + 1, line))
    else:
        print(line)


def openfiles(filenames: Iterable) -> Tuple[str, Iterator[BinaryIO]]:
    """Take an iterable of filenames and yields (filename, file object) tuples"""
    if not filenames:
        filenames = ['-']
    for filename in filenames:
        if filename == '-':
            yield 'stdin', sys.stdin.buffer
        else:
            with open(filename, 'rb') as file:
                yield filename, file


def output(filenames: Iterable, line_numbers: bool = False) -> int:
    ret_code = 0
    try:
        for filename, file in openfiles(filenames):
            lineno = 0
            for line in readdocument(file, filename):
                lprint(line, lineno, line_numbers)
            ret_code = ret_code or int(lineno == 0)
    except BrokenPipeError:
        sys.stdout = os.fdopen(1)  # suppress "Exception ignored in: [...]" when pager terminates.
    return ret_code


def main() -> None:
    parser = argparse.ArgumentParser(prog='edicat', description="Print and concatenate EDI.")
    parser.add_argument('filenames', nargs='*', help="Filename(s) or - for stdin")
    parser.add_argument("-n", "--lineno", action="store_true",
                        help="Number the output lines, starting at 1.")
    parser.add_argument('--version', action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.version:
        print("edicat", edicat.__version__)
    # This behavior diverges from cat, but is more user friendly.
    elif not args.filenames and sys.stdin.isatty():
        parser.print_help()
        sys.exit(1)
    else:
        sys.exit(output(args.filenames, args.lineno))


if __name__ == '__main__':
    main()
