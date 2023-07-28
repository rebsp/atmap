import unittest
from atmap import Atmap
from avwx import Metar, Taf

class TestAtmap(unittest.TestCase):
    def test_lszh(self):
        # corresponds to the example in the technical note (page 5)
        report = 'LSZH 221630Z VRB01KT 1000 R14/0600 SN OVC008 M2/0 Q1019'
        atmap = Atmap.from_metar(report)
        self.assertEqual(atmap.ceiling, 2)
        self.assertEqual(atmap.precip, 3)
        self.assertEqual(atmap.freezing, 4)

    def test_taf(self):
        report = 'LSZH 271125Z 2712/2818 24008KT CAVOK TX24/2715Z TN15/2805Z TX26/2813Z PROB30 TEMPO 2712/2715 9999 SCT080 TEMPO 2800/2808 9999 SCT060 BECMG 2808/2810 9999 FEW040 BECMG 2810/2813 27010KT PROB40 TEMPO 2813/2818 SHRA SCT040TCU PROB30 2815/2818 24015G30KT TSRA FEW040CB'
        taf = Atmap.from_taf(report)
        self.assertEqual(taf[1]['probability'], 30)
        self.assertEqual(taf[5]['probability'], 40)

if __name__ == '__main__':
    unittest.main()