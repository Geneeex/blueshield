"""Unit-explicit engineering functions for illustrative scenarios, not validation.

All functions consume the units stated in their parameter names. No function
selects an effective coagulant dose, predicts organism removal, or asserts safety.
"""
from __future__ import annotations

import math
from numbers import Real
from typing import Iterable


def number(value: float, name: str, *, minimum: float | None = None,
           strict: bool = False) -> float:
    """Reject nonnumeric, Boolean, nonfinite, and out-of-domain input."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    if minimum is not None and (result < minimum or (strict and result == minimum)):
        relation = ">" if strict else ">="
        raise ValueError(f"{name} must be {relation} {minimum}")
    return result


def fraction(value: float, name: str, *, allow_zero: bool = False) -> float:
    result = number(value, name, minimum=0, strict=not allow_zero)
    if result > 1:
        raise ValueError(f"{name} must be <= 1")
    return result


def batch_cycle(batch_L: float, recoverable_fraction: float, flow_L_h: float,
                rapid_min: float, floc_min: float, settle_min: float) -> dict:
    """Eq. cycle: sequential nominal timing; filling/cleaning delays omitted."""
    batch = number(batch_L, "batch_L", minimum=0, strict=True)
    recovered = fraction(recoverable_fraction, "recoverable_fraction")
    flow = number(flow_L_h, "flow_L_h", minimum=0, strict=True)
    times = [number(v, n, minimum=0) for v, n in
             [(rapid_min, "rapid_min"), (floc_min, "floc_min"), (settle_min, "settle_min")]]
    product = batch * recovered
    pretreatment_min = sum(times)
    discharge_h = product / flow
    cycle_h = pretreatment_min / 60 + discharge_h
    return {"product_L": product, "pretreatment_min": pretreatment_min,
            "discharge_h": discharge_h, "discharge_min": discharge_h * 60,
            "cycle_h": cycle_h, "cycle_average_L_h": product / cycle_h}


def coagulant_accounting(dose_mg_L: float, batch_L: float,
                         stock_mg_L: float) -> dict:
    """Eq. alum: dose and stock must use the SAME commercial-product basis."""
    dose = number(dose_mg_L, "dose_mg_L", minimum=0)
    volume = number(batch_L, "batch_L", minimum=0, strict=True)
    stock = number(stock_mg_L, "stock_mg_L", minimum=0, strict=True)
    return {"product_mass_g": dose * volume / 1000,
            "stock_volume_L": dose * volume / stock,
            "stock_volume_mL": dose * volume / stock * 1000}


def mixing_power(viscosity_Pa_s: float, volume_m3: float,
                 gradient_s_inverse: float) -> float:
    """Eq. mixing: P_water = viscosity * water volume * G**2, in watts."""
    viscosity = number(viscosity_Pa_s, "viscosity_Pa_s", minimum=0, strict=True)
    volume = number(volume_m3, "volume_m3", minimum=0, strict=True)
    gradient = number(gradient_s_inverse, "gradient_s_inverse", minimum=0)
    return viscosity * volume * gradient ** 2


def mixing_gradient(power_water_W: float, viscosity_Pa_s: float,
                    volume_m3: float) -> float:
    power = number(power_water_W, "power_water_W", minimum=0)
    viscosity = number(viscosity_Pa_s, "viscosity_Pa_s", minimum=0, strict=True)
    volume = number(volume_m3, "volume_m3", minimum=0, strict=True)
    return math.sqrt(power / (viscosity * volume))


def membrane_area(flow_L_h: float, flux_LMH: float) -> float:
    """Eq. membrane: active area in m^2, for assumed operating flux in LMH."""
    flow = number(flow_L_h, "flow_L_h", minimum=0)
    flux = number(flux_LMH, "flux_LMH", minimum=0, strict=True)
    return flow / flux


def membrane_flux(flow_L_h: float, area_m2: float) -> float:
    return number(flow_L_h, "flow_L_h", minimum=0) / number(
        area_m2, "area_m2", minimum=0, strict=True)


def apparent_permeance(flux_LMH: float, transmembrane_bar: float) -> float:
    """Applied-pressure permeance in LMH/bar; not a universal material constant."""
    return number(flux_LMH, "flux_LMH", minimum=0) / number(
        transmembrane_bar, "transmembrane_bar", minimum=0, strict=True)


def transmembrane_pressure(feed_bar: float, retentate_bar: float,
                           permeate_bar: float) -> float:
    """Approximate cross-flow TMP; input pressures share one pressure reference."""
    values = [number(v, n) for v, n in [(feed_bar, "feed_bar"),
              (retentate_bar, "retentate_bar"), (permeate_bar, "permeate_bar")]]
    return (values[0] + values[1]) / 2 - values[2]


def solute_rejection(feed_concentration: float, permeate_concentration: float) -> float:
    """Eq. membrane: fraction, using matching concentration units/assay basis.

    Negative rejection is permitted when permeate exceeds feed. No empirical
    concentration inputs are distributed in this repository.
    """
    feed = number(feed_concentration, "feed_concentration", minimum=0, strict=True)
    permeate = number(permeate_concentration, "permeate_concentration", minimum=0)
    return 1 - permeate / feed


def hydrostatic_pressure(density_kg_m3: float, gravity_m_s2: float,
                         head_m: float) -> dict:
    density = number(density_kg_m3, "density_kg_m3", minimum=0, strict=True)
    gravity = number(gravity_m_s2, "gravity_m_s2", minimum=0, strict=True)
    head = number(head_m, "head_m", minimum=0)
    pressure = density * gravity * head
    return {"pressure_Pa": pressure, "pressure_bar": pressure / 100000}


def head_from_pressure(pressure_bar: float, density_kg_m3: float,
                       gravity_m_s2: float) -> float:
    pressure = number(pressure_bar, "pressure_bar", minimum=0)
    density = number(density_kg_m3, "density_kg_m3", minimum=0, strict=True)
    gravity = number(gravity_m_s2, "gravity_m_s2", minimum=0, strict=True)
    return pressure * 100000 / (density * gravity)


def trajectory_fluence(times_s: Iterable[float], rates_mW_cm2: Iterable[float]) -> float:
    """Eq. uvpath: trapezoidal integral of sampled in-water trajectory rates.

    Samples must start at zero and increase strictly. Result is mJ/cm^2. This
    quadrature cannot create unknown trajectories or validate a UV reactor.
    """
    times = [number(v, "time_s", minimum=0) for v in times_s]
    rates = [number(v, "rate_mW_cm2", minimum=0) for v in rates_mW_cm2]
    if len(times) != len(rates) or len(times) < 2:
        raise ValueError("trajectory needs at least two paired time/rate samples")
    if times[0] != 0 or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("trajectory times must start at zero and increase strictly")
    return sum((b - a) * (ra + rb) / 2
               for a, b, ra, rb in zip(times, times[1:], rates, rates[1:]))


def ideal_uv_size(flow_L_h: float, study_fluence_mJ_cm2: float,
                  in_water_rate_mW_cm2: float) -> dict:
    """Eq. uvvolume: uniform-field, plug-flow illustration, not validated dose."""
    flow = number(flow_L_h, "flow_L_h", minimum=0, strict=True)
    fluence = number(study_fluence_mJ_cm2, "study_fluence_mJ_cm2", minimum=0, strict=True)
    rate = number(in_water_rate_mW_cm2, "in_water_rate_mW_cm2", minimum=0, strict=True)
    exposure = fluence / rate
    return {"exposure_s": exposure, "ideal_water_volume_L": flow / 3600 * exposure}


def nominal_uv_fluence(flow_L_h: float, water_volume_L: float,
                       in_water_rate_mW_cm2: float) -> float:
    flow = number(flow_L_h, "flow_L_h", minimum=0, strict=True)
    volume = number(water_volume_L, "water_volume_L", minimum=0)
    rate = number(in_water_rate_mW_cm2, "in_water_rate_mW_cm2", minimum=0)
    return rate * volume / (flow / 3600)


def pump_work(total_pressure_bar: float, pump_flow_L_h: float,
               overall_efficiency: float) -> dict:
    """Eq. energy: W and kWh/m^3 PUMPED; excludes other system loads."""
    pressure_Pa = number(total_pressure_bar, "total_pressure_bar", minimum=0) * 100000
    flow_m3_s = number(pump_flow_L_h, "pump_flow_L_h", minimum=0) / 1000 / 3600
    efficiency = fraction(overall_efficiency, "overall_efficiency")
    return {"power_W": pressure_Pa * flow_m3_s / efficiency,
            "specific_energy_kWh_m3_pumped": pressure_Pa / (3600000 * efficiency)}


def log_reduction(inlet_concentration: float, outlet_concentration: float) -> float:
    """Eq. lrv, only for matching viable/infective organism and assay bases.

    Zero/nondetect output is invalid: use a documented detection limit and report
    a bound instead. No BLUESHIELD concentration measurements are supplied.
    """
    inlet = number(inlet_concentration, "inlet_concentration", minimum=0, strict=True)
    outlet = number(outlet_concentration, "outlet_concentration", minimum=0, strict=True)
    return math.log10(inlet) - math.log10(outlet)


def removal_fraction_from_lrv(lrv: float) -> float:
    value = number(lrv, "lrv")
    try:
        return 1 - 10 ** (-value)
    except OverflowError as exc:
        raise ValueError("lrv magnitude exceeds floating-point range") from exc


def quantity(inputs: dict, group: str, key: str, unit: str):
    """Read an input only when its units and provenance are explicit."""
    entry = inputs[group][key]
    if entry.get("unit") != unit:
        raise ValueError(f"{group}.{key}: expected unit {unit!r}")
    if not entry.get("source") or entry.get("status") != "illustrative_assumption":
        raise ValueError(f"{group}.{key}: missing assumption status or provenance")
    return entry["value"]


EQUATIONS = [
    {"id": "cycle", "number": 1, "formula": "Vp=fr*Vb; tcycle=trapid+tfloc+tsettle+Vp/Qp; Qaverage=Vp/tcycle", "status": "illustrative_scenario", "caution": "Sequential batch; excludes filling, cleaning and operator delays; recovery is a lumped allowance."},
    {"id": "alum", "number": 2, "formula": "ma_g=D_mg_L*Vb_L/1000; Vs_L=D_mg_L*Vb_L/Cs_mg_L", "status": "illustrative_scenario", "caution": "Product mass and elemental aluminium are different bases; effective dose needs jar testing."},
    {"id": "mixing", "number": 3, "formula": "G=sqrt(Pwater/(mu*V)); Pwater=mu*V*G^2", "status": "illustrative_scenario", "caution": "Fluid power is not motor demand, impeller speed or local floc shear."},
    {"id": "membrane", "number": 4, "formula": "J=Qp/Am; Lp_app=J/TMP; R=1-Cp/Cf", "status": "illustrative_sizing_with_rejection_function_only", "caution": "No concentration measurements; flux/permeance assumptions do not predict rejection or durability."},
    {"id": "head", "number": 5, "formula": "pressure_Pa=rho*g*h; pressure_bar=pressure_Pa/100000", "status": "illustrative_scenario", "caution": "Linear permeance extrapolation neglects losses; not a validated low-pressure flux prediction."},
    {"id": "uvpath", "number": 6, "formula": "Hj=integral(Ef(xj(t),t),dt)", "status": "function_only_no_trajectory_data", "caution": "Sampled trajectories may be integrated by trapezoids; none are supplied as experimental data."},
    {"id": "uvvolume", "number": 7, "formula": "Hnom=Ebar*V/(Q_L_h/3600); Videal_L=(Q_L_h/3600)*Hstudy/Ebar", "status": "illustrative_scenario", "caution": "Uniform field and plug flow; assumed fluence is not a universal safety threshold or validated dose."},
    {"id": "energy", "number": 8, "formula": "Pel=total_pressure_Pa*Qpump_m3_s/efficiency; epump=total_pressure_Pa/(3.6e6*efficiency)", "status": "illustrative_scenario", "caution": "Energy per m^3 pumped, not full treatment energy per delivered volume."},
    {"id": "lrv", "number": 9, "formula": "LRV=log10(Nin/Nout); removal_fraction=1-10^(-LRV)", "status": "function_only_no_treatment_measurements", "caution": "Matching organism/assay basis is required; a nondetect is not zero; no BLUESHIELD removal is calculated."}
]


def calculate_scenarios(inputs: dict) -> dict:
    """Reproduce explicitly assumed manuscript examples for all relevant groups."""
    q = lambda group, key, unit: quantity(inputs, group, key, unit)
    batch = q("cycle", "batch_volume", "L")
    recovered = q("cycle", "recoverable_fraction", "fraction")
    flow = q("cycle", "discharge_flow", "L/h")
    timing = [q("cycle", key, "min") for key in
              ["rapid_mixing_time", "flocculation_time", "settling_time"]]
    density = q("head", "water_density", "kg/m^3")
    gravity = q("head", "gravity", "m/s^2")
    head = hydrostatic_pressure(density, gravity, q("head", "hydrostatic_head", "m"))
    assumed_permeance = number(q("membrane", "hypothetical_apparent_permeance", "L/(m^2*h*bar)"), "permeance", minimum=0, strict=True)
    hypothetical_flux = assumed_permeance * head["pressure_bar"]
    baseline_flux = q("membrane", "baseline_flux", "L/(m^2*h)")
    baseline_area = membrane_area(flow, baseline_flux)
    flux_remaining = fraction(q("membrane", "remaining_flux_fraction", "fraction"), "remaining_flux_fraction", allow_zero=True)
    result = {"status": "deterministic_illustrative_calculations_not_experimental_results",
              "source": inputs["source"], "equation_group_count": len(EQUATIONS),
              "cycle": batch_cycle(batch, recovered, flow, *timing),
              "alum": [{"assumed_product_dose_mg_L": d, **coagulant_accounting(d, batch, q("alum", "stock_concentration", "mg/L same commercial product"))}
                       for d in q("alum", "product_doses", "mg/L commercial product")],
              "mixing": [{"assumed_gradient_s_inverse": g, "fluid_power_W": mixing_power(q("mixing", "dynamic_viscosity", "Pa*s"), q("mixing", "water_volume", "m^3"), g)}
                         for g in q("mixing", "velocity_gradients", "1/s")],
              "membrane": {"area_scenarios": [{"assumed_flux_LMH": j, "active_area_m2": membrane_area(flow, j)} for j in q("membrane", "operating_fluxes", "L/(m^2*h)")],
                           "fouling_scenario": {"baseline_area_m2": baseline_area, "remaining_flux_LMH": baseline_flux * flux_remaining, "flow_after_decline_L_h": baseline_area * baseline_flux * flux_remaining},
                           "rejection": {"calculated": False, "reason": "No paired concentration measurements supplied."}},
              "head": {**head, "comparison_water_head_m": head_from_pressure(q("head", "comparison_pressure", "bar"), density, gravity), "hypothetical_linear_flux_LMH": hypothetical_flux, "hypothetical_required_area_m2": membrane_area(flow, hypothetical_flux)},
              "uvpath": {"calculated": False, "reason": "No in-water trajectory measurements supplied; trajectory_fluence implements sampled quadrature."},
              "uvvolume": [{"assumed_in_water_rate_mW_cm2": e, **ideal_uv_size(flow, q("uvvolume", "study_fluence", "mJ/cm^2"), e)} for e in q("uvvolume", "in_water_fluence_rates", "mW/cm^2")],
              "energy": [{"assumed_total_pressure_bar": p, **pump_work(p, q("energy", "pump_flow", "L/h"), q("energy", "overall_efficiency", "fraction"))} for p in q("energy", "total_pressure_differentials", "bar")],
              "lrv": {"calculated": False, "reason": "No BLUESHIELD microbial inlet/outlet measurements supplied; formulas only."}}
    return result


def linspace(start: float, stop: float, points: int) -> list[float]:
    a, b = number(start, "start"), number(stop, "stop")
    if isinstance(points, bool) or not isinstance(points, int) or points < 2 or b <= a:
        raise ValueError("linspace needs increasing endpoints and integer points >= 2")
    return [a + (b - a) * i / (points - 1) for i in range(points)]


def sensitivity_rows(inputs: dict) -> tuple[list[dict], list[dict]]:
    q = lambda group, key, unit: quantity(inputs, group, key, unit)
    flows = linspace(*q("sensitivity", "discharge_flow_range", "L/h min,max,points"))
    fluxes = linspace(*q("sensitivity", "flux_range", "L/(m^2*h) min,max,points"))
    batch, recovery = q("cycle", "batch_volume", "L"), q("cycle", "recoverable_fraction", "fraction")
    timing = [q("cycle", key, "min") for key in ["rapid_mixing_time", "flocculation_time", "settling_time"]]
    cycle_rows = [{"assumed_discharge_L_h": f, "calculated_cycle_average_L_h": batch_cycle(batch, recovery, f, *timing)["cycle_average_L_h"], "status": "illustrative_calculation"} for f in flows]
    membrane_rows = [{"assumed_flux_LMH": j, "calculated_active_area_m2": membrane_area(q("cycle", "discharge_flow", "L/h"), j), "status": "illustrative_calculation"} for j in fluxes]
    return cycle_rows, membrane_rows
