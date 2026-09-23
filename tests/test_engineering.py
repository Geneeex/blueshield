"""Synthetic software test inputs are unit fixtures, never study measurements."""
import copy
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from blueshield import engineering as e


class EngineeringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = json.loads((ROOT / "data" / "engineering_inputs.json").read_text(encoding="utf-8"))

    def test_batch_manuscript_minutes_and_hours(self):
        result = e.batch_cycle(20, 0.9, 10, 1, 20, 60)
        self.assertEqual(result["product_L"], 18)
        self.assertEqual(result["pretreatment_min"], 81)
        self.assertEqual(result["discharge_min"], 108)
        self.assertAlmostEqual(result["cycle_h"], 3.15)
        self.assertAlmostEqual(result["cycle_average_L_h"], 40 / 7)

    def test_batch_limiting_cases_and_flow_monotonicity(self):
        zero_wait = e.batch_cycle(20, 1, 10, 0, 0, 0)
        self.assertEqual(zero_wait["cycle_average_L_h"], 10)
        slow = e.batch_cycle(20, 0.9, 5, 1, 20, 60)
        fast = e.batch_cycle(20, 0.9, 10, 1, 20, 60)
        self.assertLess(slow["cycle_average_L_h"], fast["cycle_average_L_h"])
        self.assertLess(fast["cycle_average_L_h"], 10)

    def test_invalid_batch_inputs(self):
        for args in [(0, .9, 10, 1, 20, 60), (20, 1.1, 10, 1, 20, 60),
                     (20, 0, 10, 1, 20, 60), (20, .9, 0, 1, 20, 60),
                     (20, .9, 10, -1, 20, 60)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                e.batch_cycle(*args)

    def test_coagulant_mass_and_stock_units(self):
        for dose, mass, stock_mL in [(10, .2, 20), (30, .6, 60), (50, 1, 100)]:
            result = e.coagulant_accounting(dose, 20, 10000)
            self.assertAlmostEqual(result["product_mass_g"], mass)
            self.assertAlmostEqual(result["stock_volume_mL"], stock_mL)
            self.assertAlmostEqual(result["stock_volume_L"] * 10000 / 1000, mass)

    def test_coagulant_zero_and_invalid_stock(self):
        self.assertEqual(e.coagulant_accounting(0, 20, 10000)["product_mass_g"], 0)
        with self.assertRaises(ValueError):
            e.coagulant_accounting(10, 20, 0)

    def test_mixing_fluid_power_and_inverse(self):
        self.assertAlmostEqual(e.mixing_power(.001, .02, 700), 9.8)
        self.assertAlmostEqual(e.mixing_power(.001, .02, 50), .05)
        self.assertAlmostEqual(e.mixing_gradient(9.8, .001, .02), 700)

    def test_mixing_volume_conversion(self):
        self.assertAlmostEqual(e.mixing_power(.001, 20 / 1000, 700), 9.8)
        with self.assertRaises(ValueError):
            e.mixing_power(0, .02, 700)

    def test_membrane_area_flux_inverse(self):
        for flux, expected_area in [(10, 1), (25, .4), (50, .2)]:
            area = e.membrane_area(10, flux)
            self.assertAlmostEqual(area, expected_area)
            self.assertAlmostEqual(e.membrane_flux(10, area), flux)

    def test_membrane_pressure_is_not_total_pump_differential(self):
        self.assertAlmostEqual(e.transmembrane_pressure(2, 1.6, .1), 1.7)
        self.assertAlmostEqual(e.apparent_permeance(25, 2), 12.5)
        with self.assertRaises(ValueError):
            e.apparent_permeance(25, 0)

    def test_rejection_function_and_negative_rejection(self):
        self.assertAlmostEqual(e.solute_rejection(100, 10), .9)
        self.assertAlmostEqual(e.solute_rejection(100, 110), -.1)
        with self.assertRaises(ValueError):
            e.solute_rejection(0, 1)

    def test_hydrostatic_pascal_bar_and_inverse(self):
        result = e.hydrostatic_pressure(1000, 9.81, .5)
        self.assertEqual(result["pressure_Pa"], 4905)
        self.assertAlmostEqual(result["pressure_bar"], .04905)
        self.assertAlmostEqual(e.head_from_pressure(result["pressure_bar"], 1000, 9.81), .5)
        self.assertAlmostEqual(e.head_from_pressure(1, 1000, 9.81), 10.19367991845056)

    def test_uv_path_constant_and_linear_quadrature(self):
        self.assertAlmostEqual(e.trajectory_fluence([0, 40], [1, 1]), 40)
        self.assertAlmostEqual(e.trajectory_fluence([0, 10, 20], [0, 1, 2]), 20)

    def test_uv_invalid_paths(self):
        for times, rates in [([0], [1]), ([0, 1], [1]), ([1, 2], [1, 1]),
                             ([0, 0], [1, 1]), ([0, 2, 1], [1, 1, 1]), ([0, 1], [-1, 1])]:
            with self.subTest(times=times, rates=rates), self.assertRaises(ValueError):
                e.trajectory_fluence(times, rates)

    def test_uv_seconds_flow_and_volume(self):
        for rate, exposure, volume in [(.25, 160, 4 / 9), (.5, 80, 2 / 9), (1, 40, 1 / 9)]:
            result = e.ideal_uv_size(10, 40, rate)
            self.assertAlmostEqual(result["exposure_s"], exposure)
            self.assertAlmostEqual(result["ideal_water_volume_L"], volume)
            self.assertAlmostEqual(e.nominal_uv_fluence(10, volume, rate), 40)

    def test_uv_zero_rate_invalid(self):
        with self.assertRaises(ValueError):
            e.ideal_uv_size(10, 40, 0)

    def test_pump_units_and_energy_conservation(self):
        for pressure in [.5, 2]:
            result = e.pump_work(pressure, 10, .3)
            expected_W = pressure * 100000 * (10 / 1000 / 3600) / .3
            self.assertAlmostEqual(result["power_W"], expected_W)
            self.assertAlmostEqual(result["power_W"] / 1000 / .01, result["specific_energy_kWh_m3_pumped"])

    def test_pump_invalid_efficiency(self):
        for efficiency in [0, -.1, 1.1]:
            with self.subTest(efficiency=efficiency), self.assertRaises(ValueError):
                e.pump_work(.5, 10, efficiency)

    def test_log_reduction_function_and_fraction(self):
        lrv = e.log_reduction(10000, 10)
        self.assertEqual(lrv, 3)
        self.assertAlmostEqual(e.removal_fraction_from_lrv(lrv), .999)
        self.assertEqual(e.log_reduction(10, 100), -1)
        self.assertEqual(e.removal_fraction_from_lrv(0), 0)

    def test_nondetect_is_not_zero(self):
        with self.assertRaises(ValueError):
            e.log_reduction(1000, 0)
        with self.assertRaises(ValueError):
            e.log_reduction(0, 10)

    def test_nonfinite_and_boolean_inputs(self):
        for invalid in [math.inf, -math.inf, math.nan, True, "20"]:
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                e.membrane_area(invalid, 25)

    def test_input_unit_and_provenance_validation(self):
        inputs = copy.deepcopy(self.inputs)
        inputs["cycle"]["batch_volume"]["unit"] = "mL"
        with self.assertRaises(ValueError):
            e.calculate_scenarios(inputs)
        inputs = copy.deepcopy(self.inputs)
        inputs["cycle"]["batch_volume"]["source"] = ""
        with self.assertRaises(ValueError):
            e.calculate_scenarios(inputs)

    def test_all_nine_groups_and_unmeasured_endpoints(self):
        result = e.calculate_scenarios(self.inputs)
        self.assertEqual(len(e.EQUATIONS), 9)
        for equation in e.EQUATIONS:
            self.assertIn(equation["id"], result)
        self.assertFalse(result["lrv"]["calculated"])
        self.assertFalse(result["uvpath"]["calculated"])
        self.assertFalse(result["membrane"]["rejection"]["calculated"])
        self.assertAlmostEqual(result["membrane"]["fouling_scenario"]["flow_after_decline_L_h"], 5)
        self.assertAlmostEqual(result["head"]["hypothetical_required_area_m2"], 8.154943934760448)

    def test_sensitivity_rows_are_bounded_and_monotonic(self):
        cycle, area = e.sensitivity_rows(self.inputs)
        self.assertEqual((len(cycle), len(area)), (200, 220))
        self.assertTrue(all(0 < row["calculated_cycle_average_L_h"] < row["assumed_discharge_L_h"] for row in cycle))
        self.assertTrue(all(a["calculated_active_area_m2"] > b["calculated_active_area_m2"] for a, b in zip(area, area[1:])))
        with self.assertRaises(ValueError):
            e.linspace(5, 1, 20)


if __name__ == "__main__":
    unittest.main()
