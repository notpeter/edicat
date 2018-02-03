# edicat: Print and transform EDI

![build-status](https://circleci.com/gh/notpeter/edicat.svg?style=shield&circle-token=:circle-token)
![pypi-version](https://img.shields.io/pypi/v/edicat.svg)

## Why?

EDI often does not include newlines which makes it incompatible with
normal UNIX tools that operate on a line-by-line basis.  So we do some
simple detection of the segment terminator and append newlines as required.

## Install

```
pip3 install -U edicat
```

## Usage

```shell
$ edicat --help
usage: edicat [-n] [filenames [filenames ...]]

Print and concatenate EDI.

positional arguments:
  filenames     Filename(s) or - for stdin

optional arguments:
  -n, --lineno  Number the output lines, starting at 1.
```

## Examples
Simple cat:
```shell
$ cat edi850_sample.txt
ISA*00*          *00*          *01*0011223456     *01*999999999      *950120*0147*U*00300*000000005*0*P*^~GS*PO*0011223456*999999999*950120*0147*5*X*003040~ST*850*000000001~BEG*00*SA*95018017***950118~N1*SE*UNIVERSAL WIDGETS~N3*375 PLYMOUTH PARK*SUITE 205~N4*IRVING*TX*75061~N1*ST*JIT MANUFACTURING~N3*BUILDING 3B*2001 ENTERPRISE PARK~N4*JUAREZ*CH**MEX~N1*AK*JIT MANUFACTURING~N3*400 INDUSTRIAL PARKWAY~N4*INDUSTRIAL AIRPORT*KS*66030~N1*BT*JIT MANUFACTURING~N2*ACCOUNTS  PAYABLE DEPARTMENT~N3*400 INDUSTRIAL PARKWAY~N4*INDUSTRIAL AIRPORT*KS*66030~PO1*001*4*EA*330*TE*IN*525*VN*X357-W2~PID*F****HIGH PERFORMANCE WIDGET~SCH*4*EA****002*950322~CTT*1*1~SE*20*000000001~GE*1*5~IEA*1*000000005~
```

EDIcat:
```shell
$ edicat edi850_sample.txt
ISA*00*          *00*          *01*0011223456     *01*999999999      *950120*0147*U*00300*000000005*0*P*^~
GS*PO*0011223456*999999999*950120*0147*5*X*003040~
ST*850*000000001~
BEG*00*SA*95018017***950118~
N1*SE*UNIVERSAL WIDGETS~
N3*375 PLYMOUTH PARK*SUITE 205~
N4*IRVING*TX*75061~
N1*ST*JIT MANUFACTURING~
N3*BUILDING 3B*2001 ENTERPRISE PARK~
N4*JUAREZ*CH**MEX~
N1*AK*JIT MANUFACTURING~
N3*400 INDUSTRIAL PARKWAY~
N4*INDUSTRIAL AIRPORT*KS*66030~
N1*BT*JIT MANUFACTURING~
N2*ACCOUNTS  PAYABLE DEPARTMENT~
N3*400 INDUSTRIAL PARKWAY~
N4*INDUSTRIAL AIRPORT*KS*66030~
PO1*001*4*EA*330*TE*IN*525*VN*X357-W2~
PID*F****HIGH PERFORMANCE WIDGET~
SCH*4*EA****002*950322~
CTT*1*1~
SE*20*000000001~
GE*1*5~
IEA*1*000000005~
```

## Known Issues:

* `cat /path/* | edicat` won't work with documents that are mixed spec/separators (stdin has no hints as to file boundary).
  * Workarounds:
    * `edicat /path/*.edi`
    * `find /path/ -name '*.edi' | xargs edicat`
* No TRADACOMS support
* No HL7 support
