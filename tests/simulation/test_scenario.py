"""Tests for the backend-agnostic DEM scenario (no YADE needed)."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from pm_dem_sm.simulation.scenario import SimulationScenario, load_scenario

# --- Setup -------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_FILES = sorted((REPO_ROOT / "configs" / "simulation").glob("*.json"))


# --- Tests -------------------------------------------------------------------


def test_defaults_round_trip_through_dict():
    s = SimulationScenario()
    assert SimulationScenario.from_dict(s.to_dict()).to_dict() == s.to_dict()


def test_to_dict_is_json_serializable():
    json.dumps(SimulationScenario().to_dict())


@pytest.mark.parametrize("path", SCENARIO_FILES, ids=lambda p: p.name)
def test_packaged_scenarios_load(path):
    s = load_scenario(path)
    assert s.name == path.stem


def test_partial_json_keeps_other_defaults(tmp_path):
    path = tmp_path / "s.json"
    path.write_text(json.dumps({"mill": {"speed_rpm": 7.5}}), encoding="utf-8")
    s = load_scenario(path)
    assert s.mill.speed_rpm == 7.5
    assert s.mill.depth_m == SimulationScenario().mill.depth_m


def test_unknown_key_raises():
    with pytest.raises(ValueError, match="Unknown"):
        SimulationScenario.from_dict({"mill": {"not_a_field": 1}})


def test_bad_choice_raises():
    with pytest.raises(ValueError, match="mill.source"):
        SimulationScenario.from_dict({"mill": {"source": "cad"}})


def test_species_material_must_exist():
    data = SimulationScenario().to_dict()
    data["species"][0]["material"] = "granite"
    with pytest.raises(ValueError, match="granite"):
        SimulationScenario.from_dict(data)


def test_overlapping_lifters_raise():
    with pytest.raises(ValueError, match="Lifters overlap"):
        SimulationScenario.from_dict(
            {"mill": {"source": "parametric", "diameter_m": 1.0, "n_lifters": 40,
                      "lifter_base_width_m": 0.2}}
        )


def test_small_and_large_species():
    s = SimulationScenario()
    assert s.small.radius_m < s.large.radius_m


def test_restitution_lookup_is_order_independent():
    s = SimulationScenario()
    assert s.restitution_for("rock", "steel") == s.restitution_for("steel", "rock")


def test_critical_speed_matches_classic_formula():
    s = SimulationScenario.from_dict({"mill": {"diameter_m": 11.9}})
    d_large = 2 * s.large.radius_m
    assert s.critical_speed_rpm() == pytest.approx(42.3 / math.sqrt(11.9 - d_large), rel=1e-3)


def test_rayleigh_dt_scales_with_young():
    soft = SimulationScenario.from_dict({"solver": {"young_scale": 0.01}})
    assert soft.rayleigh_dt_s() == pytest.approx(10 * SimulationScenario().rayleigh_dt_s())


def test_dt_above_rayleigh_warns():
    s = SimulationScenario.from_dict({"solver": {"dt_s": 1e-4}})
    assert any("Rayleigh" in w for w in s.warnings())


def test_fill_fraction_counts_both_species():
    s = SimulationScenario()
    solids = sum(sp.volume_m3 for sp in s.species)
    mill = math.pi * (s.mill.diameter_m / 2) ** 2 * s.mill.depth_m
    assert s.fill_fraction(packing=1.0) == pytest.approx(solids / mill)
