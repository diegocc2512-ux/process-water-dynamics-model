from pathlib import Path
import sys
import math

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from process_water_model.model import (
    Organism,
    gamma_aw,
    gamma_pH,
    logistic_step,
    ratkowsky_mu,
    replacement_fraction,
    run_model,
)


def test_gamma_bounds():
    assert gamma_pH(3.5, 4.0, 7.0) == 0.0
    assert gamma_pH(7.0, 4.0, 7.0) == 1.0
    assert 0 < gamma_pH(5.5, 4.0, 7.0) < 1
    assert gamma_aw(0.90, 0.94) == 0.0
    assert gamma_aw(1.0, 0.94) == 1.0


def test_ratkowsky_equation():
    org = Organism(
        "X", "Test", 1, 0, 100, 1e6,
        0.02, 5, 45, 4, 7, 0.94, 0, 0, "SYNTHETIC"
    )
    expected = (0.02 * (15 - 5)) ** 2
    assert math.isclose(ratkowsky_mu(org, 15), expected)
    assert ratkowsky_mu(org, 4) == 0.0


def test_cstr_replacement_fraction():
    f = replacement_fraction(500, 100, 100, 1.0, 1.0)
    assert math.isclose(f, 1 - math.exp(-0.2))


def test_logistic_growth_is_bounded():
    result = logistic_step(100, 0.5, 10, 1000)
    assert 100 < result <= 1000


def test_example_model_runs(tmp_path):
    rows, summary = run_model(ROOT / "config", tmp_path)
    assert rows
    assert summary
    assert {"pre_redose_residual_ppm", "post_control_residual_ppm", "redose_event"} <= set(rows[0])
    assert all(r["parameter_status"] == "DEMONSTRATION_ONLY" for r in rows)
