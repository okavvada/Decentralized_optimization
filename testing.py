import unittest
import functions
import Parameters as P

class MyTest(unittest.TestCase):
    def test_hierarchical_cluster(self):
        X = [(0,0),(0,1),(1,0),(5,0),(5,1)]
        Z_t = [[ 0.,1.,1.,2.], [3.,4.,1.,2.], [2.,5.,1.29099445,3.], [6.,7.,7.23417814,5.]]
        cluster = {1:[0,1],2:[3,4],3:[0,1,2],4:[3,4,0,1,2]}
        l = functions.hierarchical_cluster(X, Z_t)
        self.assertEqual(cluster, l)

    def test_pump_energy_building(self):
        floors = 3
        l = functions.pump_energy_building(floors)
        self.assertEqual(3*floors*P.water_weight/1000, l)

    def test_ground_elevation(self):
        building_elevation = 100
        totals_elevation = 150
        l = functions.ground_elevation(building_elevation, totals_elevation)
        self.assertEqual((totals_elevation - building_elevation), l)

    def test_ground_elevation_energy(self):
        building_elevation = 100
        totals_elevation = 150
        l = functions.ground_elevation_energy(building_elevation, totals_elevation)
        self.assertEqual((totals_elevation - building_elevation)*P.water_weight/1000, l)

    def test_calc_flow(self):
        building_pop = 5
        totals_pop = 150
        l = functions.calc_flow(building_pop, totals_pop)
        self.assertEqual((building_pop + totals_pop)*P.water_demand, l)


if __name__ == '__main__':
    unittest.main()