import unittest
from check_underground_truck import assess_bounds

class TruckIntakeTests(unittest.TestCase):
    def test_low_profile_dimensions(self):
        self.assertTrue(assess_bounds((0,0,0),(3.02,11.196,3.035))['passed'])
    def test_tall_surface_vehicle_rejected(self):
        result=assess_bounds((0,0,0),(6,11,5.1))
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['errors']),2)
    def test_wrong_units_rejected(self):
        self.assertFalse(assess_bounds((0,0,0),(302,1119,303))['passed'])
    def test_offset_does_not_change_dimensions(self):
        self.assertTrue(assess_bounds((-20,-10,-1),(-17,1,2))['passed'])

if __name__=='__main__': unittest.main()
