import argparse
import sys

from edicat.edi import EDI

def main():
    parser = argparse.ArgumentParser(description="Print and concatenate EDI.")
    parser.add_argument('edifile',
                        nargs='?',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        default=sys.stdin,
                        help="EDI Filename (or stdin)")
    args = parser.parse_args()
    if args.edifile == sys.stdin and sys.stdin.isatty():
        parser.print_help()
        sys.exit(1)
    print(EDI(args.edifile))
