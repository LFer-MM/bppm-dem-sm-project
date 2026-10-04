"""Random-mix ingress simulation for the bidisperse SAG mill slice (YADE).

Follows the ``run_<subpackage>.py`` orchestrator convention of
:mod:`bppm_dem_sm.metrics.run_metrics` and
:mod:`bppm_dem_sm.visualization.run_visualization`. Imports every concern
module unaliased (not just the ones called directly) so the ``PyRunner``
command strings inside :mod:`~bppm_dem_sm.simulation.yade_dem.engines` and
:mod:`~bppm_dem_sm.simulation.yade_dem.capture` -- evaluated by
YADE in this script's global namespace when run as ``yade run_simulation.py``
-- can resolve ``engines._balance_check()`` / ``capture._save_sphere_frame()``.
"""

from yade import qt

from ... import config
from . import capture, diagnostics, engines, materials, particles, state, stl  # noqa: F401

# --- Public functions --------------------------------------------------------


def run():
    """Set up the mill and ingress a random bidisperse particle charge.

    Initializes YADE materials, loads the SAG mill STL slice, configures
    Hertz-Mindlin contacts, opens a Qt viewer, and calls
    :func:`~bppm_dem_sm.simulation.yade_dem.particles.ingress_random` with the
    bidisperse rock/steel charge.
    """
    materials.initialize_simulation_materials(config.MATERIALS)
    stl.initialize_sag_mill_slice(config.SAGMILL_STL_PATH)
    engines.initialize_engines(
        contact_model="hertz_mindlin",
        contact_model_params=config.build_yade_material_interactions(),
        rotation_engine=False,
    )
    engines.set_dt(new_dt=0.000015 * 0.2)
    # state.load_particle_positions("rmic_nopf_settled.csv")
    engines.set_gravity_damping(new_gravity_damping=0.2)

    qt.Controller()
    qt.View()

    particles.ingress_random(
        diameter=config.MILL_DIAMETER_M,
        depth=0.375,
        r_small=0.034925,
        r_large=0.06985,
        n_small=994,
        n_large=234,
        box_height=1.0,
        material_small="rock",
        material_large="steel",
        color_small=(1, 0, 0),
        color_large=(0, 0, 1),
        settle_steps=10000000,
        padding=0.1,
    )


# Manual follow-up steps, not run automatically: uncomment, or type into the
# YADE terminal, as needed once ingress has settled.

# engines.set_gravity_damping(new_gravity_damping=0.0)

# diagnostics.check_overlaps()

# particles.get_particle_inventory(0.06985/2, 0.1397/2)

# state.load_ball_particles(s0_global_sim_config.ball_diam_m, s0_global_sim_config.ball_count)

# Run by hand in the YADE terminal:
# state.settle_balance_save(0.2, "rmic_nopf_settled.csv")

# engines.run_until_forces_balanced(threshold=0.01)

# state.save_particle_positions("rmic_nopf.csv")


# --- Script entry point ------------------------------------------------------

if __name__ == "__main__":
    run()
