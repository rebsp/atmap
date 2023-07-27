import unittest
from atmap import Atmap

class TestAtmap(unittest.TestCase):
    def test_lszh(self):
        # corresponds to the example in the technical note (page 5)
        report = 'LSZH 221630Z VRB01KT 1000 R14/0600 SN OVC008 M2/0 Q1019'
        atmap = Atmap.from_metar(report)
        self.assertEqual(atmap.ceiling, 2)
        self.assertEqual(atmap.precip, 3)
        self.assertEqual(atmap.freezing, 4)


if __name__ == '__main__':
    unittest.main()