import unittest

import edicat.edi as edi


class TestEdifact(unittest.TestCase):
    maxDiff = None

    # TODO: Better tests for '\r\n' and such.

    def test_linebreaks(self):
        po3040 = ("ISA*00*          *00*          *01*0011223456     *01*999999999      *950120*0147*U*00300*000000005*0*P*^~"  # noqa
                  "GS*PO*0011223456*999999999*950120*0147*5*X*003040~"
                  "ST*850*000000001~"
                  "BEG*00*SA*95018017***950118~"
                  "N1*SE*UNIVERSAL WIDGETS~"
                  "N3*375 PLYMOUTH PARK*SUITE 205~"
                  "N4*IRVING*TX*75061~"
                  "N1*ST*JIT MANUFACTURING~"
                  "N3*BUILDING 3B*2001 ENTERPRISE PARK~"
                  "N4*JUAREZ*CH**MEX~"
                  "N1*AK*JIT MANUFACTURING~"
                  "N3*400 INDUSTRIAL PARKWAY~"
                  "N4*INDUSTRIAL AIRPORT*KS*66030~"
                  "N1*BT*JIT MANUFACTURING~"
                  "N2*ACCOUNTS  PAYABLE DEPARTMENT~"
                  "N3*400 INDUSTRIAL PARKWAY~"
                  "N4*INDUSTRIAL AIRPORT*KS*66030~"
                  "PO1*001*4*EA*330*TE*IN*525*VN*X357-W2~"
                  "PID*F****HIGH PERFORMANCE WIDGET~"
                  "SCH*4*EA****002*950322~"
                  "CTT*1*1~"
                  "SE*20*000000001~"
                  "GE*1*5~"
                  "IEA*1*000000005~")

        po3040_lb = po3040.replace("~", "~\n").strip()
        po3040_str = "\n".join(edi.readdocument(po3040))
        self.assertEqual(po3040_lb, po3040_str)


if __name__ == '__main__':
    unittest.main()
