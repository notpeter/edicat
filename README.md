# edicat: Print and transform EDI

## Why?

EDI often does not include newlines which makes it incompatible with
normal UNIX tools that operate on a line-by-line basis.  So we do some
simple detection of the segment terminator and append newlines as required.

## Usage

```shell
$ edicat --help
usage: edicat [-h] [-n] [-v] [edifile]

Print and concatenate EDI.

positional arguments:
  edifile        EDI Filename (or stdin)

optional arguments:
  -h, --help     show this help message and exit
  -n, --lineno   Number the output lines, starting at 1.
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

* No concatenation/multiple file support. (I understand the irony)
* Each invocation assumes single EDI file (no support for mixed Edifact/X12 or streams with mixed separators)
* No EDIfact release character support
* No TRADACOMS support
* No HL7 support
