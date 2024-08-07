import unittest

import edicat.edi as edi


class TestEdifact(unittest.TestCase):

    def test_linebreaks(self):
        iatb = (
            "UNA:+.? '"
            "UNB+IATB:1+6XPPC:ZZ+LHPPC:ZZ+940101:0950+1'"
            "UNH+1+PAORES:93:1:IA'"
            "MSG+1:45'"
            "IFT+3+XYZCOMPANY AVAILABILITY'"
            "ERC+A7V:1:AMD'"
            "IFT+3+NO MORE FLIGHTS'"
            "ODI'"
            "TVL+240493:1000::1220+FRA+JFK+DL+400+C'"
            "PDI++C:3+Y::3+F::1'"
            "APD+74C:0:::6++++++6X'"
            "TVL+240493:1740::2030+JFK+MIA+DL+081+C'"
            "PDI++C:4'"
            "APD+EM2:0:1630::6+++++++DA'"
            "UNT+13+1'"
            "UNZ+1+1'"
        )
        iatb_lb = iatb.replace("'", "'\n").strip()
        iatb_str = "\n".join(edi.readdocument(iatb))
        self.assertEqual(iatb_lb, iatb_str)


if __name__ == "__main__":
    unittest.main()
