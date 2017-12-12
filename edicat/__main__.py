import argparse
import sys

from edicat.edi import EDI


def output(edi, line_numbers=False):
    if line_numbers:
        for lineno, line in enumerate(str(edi).split("\n")):
            print("{0: >6}\t{1}".format(lineno + 1, line))
    else:
        indent = 0
        for line in edi.lol:
            if line.startswith('GS') or line.startswith('ST') or line.startswith('UNG') or line.startswith('UNH'):
                indent += 1
            elif line.startswith('GE') or line.startswith('SE') or line.startswith('UNE') or line.startswith('UNT'):
                indent -= 1
            print("  " * indent, line, sep='')


def main():
    parser = argparse.ArgumentParser(prog='edicat',
                                     description="Print and concatenate EDI.")
    parser.add_argument('edifile', nargs='?',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        default=sys.stdin,
                        help="EDI Filename (or stdin)")
    parser.add_argument("-n", "--lineno", action="store_true",
                        help="Number the output lines, starting at 1.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    if args.edifile == sys.stdin and sys.stdin.isatty():
        parser.print_help()
        sys.exit(1)
    e = EDI(args.edifile)
    output(e, line_numbers=args.lineno)


if __name__ == '__main__':
    main()
