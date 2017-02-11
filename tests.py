import unittest
from functions import *
import Parameters as P


class TestMethods(unittest.TestCase):

  def test_ground_elevation(self):
    diff = ground_elevation(20, 50)
    self.assertEqual(diff, 30)

  def test_calc_water_flow(self):
    flow = calc_water_flow(20, 40)
    self.assertEqual(flow, 6)

  def test_calc_wastewater_flow(self):
    flow = calc_wastewater_flow(20, 40)
    self.assertEqual(flow, 12)

  def test_ground_elevation_energy(self):
    energy = ground_elevation_energy(20, 25, 5, 15)
    result = 5*P.water_weight*3.6/(3600 * P.pump_efficiency)
    self.assertEqual(energy, result)

  def test_pump_energy_building(self):
    energy = pump_energy_building(3, 15)
    result = 3*3*P.water_weight*3.6/(3600 * P.pump_efficiency)
    self.assertEqual(energy, result)

  def test_find_treatment_energy(self):
    flow = calc_wastewater_flow(15, 20)
    energy = find_treatment_energy(15, 20, 9.5, -0.3, 0, 0)
    result = (9.5*(flow)**(-0.3)+0*flow+0)*3.6
    self.assertEqual(energy, result)

  def test_find_treatment_embodied_energy(self):
    flow = calc_wastewater_flow(15, 20)
    energy = find_treatment_embodied_energy(15, 20, 9.5, -0.3, 0, 0, ttype=True)
    result = (9.5*(flow)**(-0.3)+0*flow+0)*3.6
    self.assertEqual(energy, result)

  def test_find_infrastructure_energy(self):
    energy = find_infrastructure_energy(15, 20, 300)
    result = 300*P.piping_embodied/P.pipe_lifetime/1277.5
    self.assertEqual(energy, result)

if __name__ == '__main__':
    unittest.main()