from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict
import csv
import json
import math


def _f(value, name: str, row: dict, default=None) -> float:
    if (value is None or str(value).strip() == "") and default is not None:
        return float(default)
    try:
        return float(value)
    except Exception as exc:
        raise ValueError(f"Invalid numeric value for '{name}' in row {row}") from exc


def _i(value, name: str, row: dict, default=None) -> int:
    return int(_f(value, name, row, default))


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


@dataclass
class WaterSystem:
    system_id: str
    system_name: str
    water_volume_l: float
    temperature_c: float
    pH: float
    water_activity: float
    cycle_time_min: float
    make_up_flow_l_h: float
    discharge_flow_l_h: float
    organic_load_index: float
    max_cycles: int


@dataclass
class Organism:
    organism_id: str
    name: str
    initial_cfu_ml: float
    replacement_water_cfu_ml: float
    action_limit_cfu_ml: float
    carrying_capacity_cfu_ml: float
    ratkowsky_b: float
    t_min_c: float
    t_max_c: float
    pH_min: float
    pH_opt: float
    aw_min: float
    lag_time_h: float
    base_death_rate_per_h: float
    validation_status: str


@dataclass
class Disinfection:
    system_id: str
    disinfectant_type: str
    minimum_residual_ppm: float
    initial_residual_ppm: float
    first_order_decay_k_per_h: float
    demand_loss_ppm_per_h: float
    redose_trigger_ppm: float
    redose_to_ppm: float
    validation_status: str


@dataclass
class CTParam:
    disinfectant_type: str
    organism_id: str
    log10_reduction_per_ppm_h: float
    max_log10_reduction_per_cycle: float
    pH_reference: float
    pH_sensitivity_per_unit: float
    temp_reference_c: float
    temp_q10: float
    organic_inhibition_coefficient: float
    validation_status: str


def load_inputs(input_dir: Path):
    water_rows = read_csv(input_dir / "water_systems.csv")
    organism_rows = read_csv(input_dir / "organisms.csv")
    contamination_rows = read_csv(input_dir / "contamination_inputs.csv")
    disinfection_rows = read_csv(input_dir / "disinfection_controls.csv")
    ct_rows = read_csv(input_dir / "ct_parameters.csv")
    scenario_rows = read_csv(input_dir / "scenarios.csv")

    waters = [
        WaterSystem(
            r["system_id"], r["system_name"],
            _f(r["water_volume_l"], "water_volume_l", r),
            _f(r["temperature_c"], "temperature_c", r),
            _f(r["pH"], "pH", r),
            _f(r["water_activity"], "water_activity", r),
            _f(r["cycle_time_min"], "cycle_time_min", r),
            _f(r["make_up_flow_l_h"], "make_up_flow_l_h", r),
            _f(r["discharge_flow_l_h"], "discharge_flow_l_h", r),
            _f(r["organic_load_index"], "organic_load_index", r),
            _i(r["max_cycles"], "max_cycles", r),
        )
        for r in water_rows
    ]

    organisms = [
        Organism(
            r["organism_id"], r["name"],
            _f(r["initial_cfu_ml"], "initial_cfu_ml", r),
            _f(r["replacement_water_cfu_ml"], "replacement_water_cfu_ml", r),
            _f(r["action_limit_cfu_ml"], "action_limit_cfu_ml", r),
            _f(r["carrying_capacity_cfu_ml"], "carrying_capacity_cfu_ml", r),
            _f(r["ratkowsky_b"], "ratkowsky_b", r),
            _f(r["t_min_c"], "t_min_c", r),
            _f(r["t_max_c"], "t_max_c", r),
            _f(r["pH_min"], "pH_min", r),
            _f(r["pH_opt"], "pH_opt", r),
            _f(r["aw_min"], "aw_min", r),
            _f(r["lag_time_h"], "lag_time_h", r),
            _f(r["base_death_rate_per_h"], "base_death_rate_per_h", r),
            r.get("validation_status", "SYNTHETIC"),
        )
        for r in organism_rows
    ]

    contamination = {
        (r["system_id"], r["organism_id"]):
            _f(r["contamination_input_cfu_per_cycle"], "contamination_input_cfu_per_cycle", r)
        for r in contamination_rows
    }

    disinfection = {
        r["system_id"]: Disinfection(
            r["system_id"], r["disinfectant_type"].upper(),
            _f(r["minimum_residual_ppm"], "minimum_residual_ppm", r),
            _f(r["initial_residual_ppm"], "initial_residual_ppm", r),
            _f(r["first_order_decay_k_per_h"], "first_order_decay_k_per_h", r),
            _f(r["demand_loss_ppm_per_h"], "demand_loss_ppm_per_h", r),
            _f(r["redose_trigger_ppm"], "redose_trigger_ppm", r),
            _f(r["redose_to_ppm"], "redose_to_ppm", r),
            r.get("validation_status", "SYNTHETIC"),
        )
        for r in disinfection_rows
    }

    ct_params = {
        (r["disinfectant_type"].upper(), r["organism_id"]): CTParam(
            r["disinfectant_type"].upper(), r["organism_id"],
            _f(r["log10_reduction_per_ppm_h"], "log10_reduction_per_ppm_h", r),
            _f(r["max_log10_reduction_per_cycle"], "max_log10_reduction_per_cycle", r),
            _f(r["pH_reference"], "pH_reference", r),
            _f(r["pH_sensitivity_per_unit"], "pH_sensitivity_per_unit", r),
            _f(r["temp_reference_c"], "temp_reference_c", r),
            _f(r["temp_q10"], "temp_q10", r),
            _f(r["organic_inhibition_coefficient"], "organic_inhibition_coefficient", r),
            r.get("validation_status", "SYNTHETIC"),
        )
        for r in ct_rows
    }

    scenarios = [
        {
            "scenario_id": r["scenario_id"],
            "contamination_multiplier": _f(r["contamination_multiplier"], "contamination_multiplier", r),
            "growth_multiplier": _f(r["growth_multiplier"], "growth_multiplier", r),
            "decay_multiplier": _f(r["decay_multiplier"], "decay_multiplier", r),
            "flow_multiplier": _f(r["flow_multiplier"], "flow_multiplier", r),
        }
        for r in scenario_rows
    ]
    return waters, organisms, contamination, disinfection, ct_params, scenarios


def gamma_pH(pH: float, pH_min: float, pH_opt: float) -> float:
    if pH <= pH_min:
        return 0.0
    if pH >= pH_opt:
        return 1.0
    return max(0.0, min(1.0, (pH - pH_min) / (pH_opt - pH_min)))


def gamma_aw(aw: float, aw_min: float) -> float:
    if aw <= aw_min:
        return 0.0
    return max(0.0, min(1.0, (aw - aw_min) / (1.0 - aw_min)))


def ratkowsky_mu(org: Organism, temperature_c: float) -> float:
    """Sub-optimal square-root model: sqrt(mu) = b (T - Tmin)."""
    if (
        temperature_c <= org.t_min_c
        or temperature_c >= org.t_max_c
        or org.ratkowsky_b <= 0
    ):
        return 0.0
    return (org.ratkowsky_b * (temperature_c - org.t_min_c)) ** 2


def effective_growth_rate(
    org: Organism, water: WaterSystem, scenario: dict, elapsed_h: float
) -> float:
    if elapsed_h < org.lag_time_h:
        return -org.base_death_rate_per_h

    growth = (
        ratkowsky_mu(org, water.temperature_c)
        * gamma_pH(water.pH, org.pH_min, org.pH_opt)
        * gamma_aw(water.water_activity, org.aw_min)
        * scenario["growth_multiplier"]
    )
    return growth - org.base_death_rate_per_h


def logistic_step(n: float, mu: float, dt_h: float, carrying_capacity: float) -> float:
    if n <= 0:
        return 0.0
    if mu <= 0:
        return n * math.exp(mu * dt_h)

    K = max(carrying_capacity, n)
    exponential = math.exp(min(50.0, mu * dt_h))
    return K * n * exponential / (K + n * (exponential - 1.0))


def ct_log_reduction(
    water: WaterSystem,
    ct: CTParam | None,
    residual_ppm: float,
    dt_h: float,
) -> float:
    if ct is None or residual_ppm <= 0:
        return 0.0

    pH_factor = math.exp(
        -ct.pH_sensitivity_per_unit * (water.pH - ct.pH_reference)
    )
    temperature_factor = ct.temp_q10 ** (
        (water.temperature_c - ct.temp_reference_c) / 10.0
    )
    organic_factor = 1.0 / (
        1.0
        + max(0.0, water.organic_load_index)
        * max(0.0, ct.organic_inhibition_coefficient)
    )

    reduction = (
        ct.log10_reduction_per_ppm_h
        * residual_ppm
        * dt_h
        * pH_factor
        * temperature_factor
        * organic_factor
    )
    return max(0.0, min(ct.max_log10_reduction_per_cycle, reduction))


def replacement_fraction(
    volume_l: float,
    make_up_flow_l_h: float,
    discharge_flow_l_h: float,
    dt_h: float,
    scenario_flow_multiplier: float,
) -> float:
    """Balanced-flow CSTR replacement fraction over one time step."""
    if volume_l <= 0:
        return 0.0
    flow = max(0.0, min(make_up_flow_l_h, discharge_flow_l_h))
    flow *= scenario_flow_multiplier
    return 1.0 - math.exp(-(flow / volume_l) * dt_h)


def decay_residual(
    current_ppm: float,
    control: Disinfection,
    scenario: dict,
    dt_h: float,
) -> float:
    decayed = current_ppm * math.exp(
        -control.first_order_decay_k_per_h
        * scenario["decay_multiplier"]
        * dt_h
    )
    decayed -= (
        control.demand_loss_ppm_per_h
        * scenario["decay_multiplier"]
        * dt_h
    )
    return max(0.0, decayed)


def simulate_system(
    water: WaterSystem,
    organisms: list[Organism],
    contamination: Dict[tuple[str, str], float],
    control: Disinfection,
    ct_params: Dict[tuple[str, str], CTParam],
    scenario: dict,
) -> list[dict]:
    state = {o.organism_id: o.initial_cfu_ml for o in organisms}
    residual = control.initial_residual_ppm
    dt_h = water.cycle_time_min / 60.0
    rows: list[dict] = []

    for cycle in range(water.max_cycles + 1):
        elapsed_h = cycle * dt_h

        # Current state at the beginning of the cycle
        pre_cycle_residual = residual

        if cycle < water.max_cycles:
            for org in organisms:
                mu = effective_growth_rate(org, water, scenario, elapsed_h)

                n = logistic_step(
                    state[org.organism_id],
                    mu,
                    dt_h,
                    org.carrying_capacity_cfu_ml,
                )

                ct = ct_params.get((control.disinfectant_type, org.organism_id))
                log_reduction = ct_log_reduction(water, ct, residual, dt_h)
                n *= 10 ** (-log_reduction)

                added_cfu = (
                    contamination.get((water.system_id, org.organism_id), 0.0)
                    * scenario["contamination_multiplier"]
                )
                n += added_cfu / (water.water_volume_l * 1000.0)

                fraction = replacement_fraction(
                    water.water_volume_l,
                    water.make_up_flow_l_h,
                    water.discharge_flow_l_h,
                    dt_h,
                    scenario["flow_multiplier"],
                )
                n = (
                    (1.0 - fraction) * n
                    + fraction * org.replacement_water_cfu_ml
                )
                state[org.organism_id] = max(0.0, n)

            # Residual decay is calculated before any control action.
            pre_redose_residual = decay_residual(
                residual, control, scenario, dt_h
            )
            redose_event = pre_redose_residual <= control.redose_trigger_ppm
            residual = (
                control.redose_to_ppm
                if redose_event
                else pre_redose_residual
            )
        else:
            pre_redose_residual = residual
            redose_event = False

        for org in organisms:
            concentration = state[org.organism_id]
            rows.append(
                {
                    "scenario_id": scenario["scenario_id"],
                    "system_id": water.system_id,
                    "system_name": water.system_name,
                    "cycle": cycle,
                    "elapsed_time_h": round(elapsed_h, 6),
                    "organism_id": org.organism_id,
                    "organism_name": org.name,
                    "cfu_ml": concentration,
                    "log10_cfu_ml": (
                        "" if concentration <= 0 else math.log10(concentration)
                    ),
                    "temperature_c": water.temperature_c,
                    "pH": water.pH,
                    "water_activity": water.water_activity,
                    "organic_load_index": water.organic_load_index,
                    "pre_cycle_residual_ppm": pre_cycle_residual,
                    "pre_redose_residual_ppm": pre_redose_residual,
                    "post_control_residual_ppm": residual,
                    "minimum_residual_ppm": control.minimum_residual_ppm,
                    "residual_below_minimum_before_redose": (
                        pre_redose_residual < control.minimum_residual_ppm
                    ),
                    "redose_event": redose_event,
                    "micro_action_limit_cfu_ml": org.action_limit_cfu_ml,
                    "micro_action_limit_exceeded": (
                        concentration >= org.action_limit_cfu_ml
                    ),
                    "parameter_status": (
                        "DEMONSTRATION_ONLY"
                        if (
                            org.validation_status.upper() != "VALIDATED"
                            or control.validation_status.upper() != "VALIDATED"
                        )
                        else "VALIDATED"
                    ),
                }
            )
    return rows


def summarise(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        grouped.setdefault(
            (row["scenario_id"], row["system_id"]), []
        ).append(row)

    summaries = []
    for (scenario, system_id), group in grouped.items():
        redose_cycles = sorted(
            {
                row["cycle"]
                for row in group
                if row["redose_event"]
            }
        )
        low_residual_cycles = sorted(
            {
                row["cycle"]
                for row in group
                if row["residual_below_minimum_before_redose"]
            }
        )
        micro_failure_cycles = sorted(
            {
                row["cycle"]
                for row in group
                if row["micro_action_limit_exceeded"]
            }
        )
        summaries.append(
            {
                "scenario_id": scenario,
                "system_id": system_id,
                "system_name": group[0]["system_name"],
                "redose_events": len(redose_cycles),
                "first_low_residual_cycle": (
                    "" if not low_residual_cycles else low_residual_cycles[0]
                ),
                "first_micro_action_cycle": (
                    "" if not micro_failure_cycles else micro_failure_cycles[0]
                ),
                "minimum_pre_redose_residual_ppm": min(
                    row["pre_redose_residual_ppm"] for row in group
                ),
                "status": "DEMONSTRATION / NOT VALIDATED",
            }
        )
    return summaries


def run_model(input_dir: Path, output_dir: Path) -> tuple[list[dict], list[dict]]:
    waters, organisms, contamination, controls, ct_params, scenarios = load_inputs(
        input_dir
    )
    rows: list[dict] = []
    for scenario in scenarios:
        for water in waters:
            rows.extend(
                simulate_system(
                    water,
                    organisms,
                    contamination,
                    controls[water.system_id],
                    ct_params,
                    scenario,
                )
            )

    summary = summarise(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "results_by_cycle.csv", rows)
    write_csv(output_dir / "summary.csv", summary)
    (output_dir / "run_metadata.json").write_text(
        json.dumps(
            {
                "model_version": "1.0.0-public",
                "data_status": "synthetic demonstration dataset",
                "purpose": "portfolio / validation-support demonstration",
                "warning": (
                    "Do not use example outputs as food-safety or operating limits."
                ),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return rows, summary
