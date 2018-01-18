import argparse
import sys
from typing import Iterable, Iterator, BinaryIO


import edicat
from edicat.edi import readdocument


def lprint(line: str, lineno: int, line_numbers: bool = False) -> None:
    """Print a line with optional line number"""
    if line_numbers:
        print("{0: >6}\t{1}".format(lineno + 1, line))
    else:
        print(line)


def openfiles(filenames: Iterable) -> Iterator[BinaryIO]:
    """Take an iterable of filesnames and yields file objects."""
    if not filenames:
        filenames = ['-']
    for filename in filenames:
        if filename == '-':
            yield sys.stdin.buffer
        else:
            with open(filename, 'rb') as file:
                yield file


def output(filenames: Iterable, line_numbers: bool = False) -> None:
    for file in openfiles(filenames):
        for lineno, line in enumerate(readdocument(file)):
            lprint(line, lineno, line_numbers)


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
        output(args.filenames, args.lineno)


if __name__ == '__main__':
    main()
