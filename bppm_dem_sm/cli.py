"""Command-line interface for the bidisperse DEM surrogate-model toolkit.

Two subcommands, matching the project's two runtimes:

- ``dem-sim``: launches a DEM simulation as a subprocess (``--dem-backend
  yade``, the default, requires YADE installed and on PATH; ``blaze`` is not
  implemented yet). Never imports a DEM engine's own Python API itself --
  see :mod:`bppm_dem_sm.simulation.launcher`.
- ``ml-pipeline``: runs the experiment pipeline (simulate / process / train /
  predict / metrics / visualization). Config can be supplied either as
  individual flags or as a JSON file via ``--config``. When ``--config`` is
  set, all other pipeline config flags are ignored. Flags stay flat
  (``--epochs``); they are mapped onto nested option groups on
  :class:`~bppm_dem_sm.config.ExperimentConfig`.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import fields
from pathlib import Path
from typing import Any, get_type_hints

from .config import DEM_BACKENDS, ExperimentConfig, _option_group_types
from .experiment_pipeline import run_experiment_pipeline
from .simulation import launcher

# --- Constants ---------------------------------------------------------------

# Fields with a hand-written flag instead of the generic per-field one.
_SKIP_CLI_FIELDS = frozenset({"feature_cols"})


# --- Public functions --------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level ``bppm-dem-sm`` parser with its two subcommands.

    Returns:
        argparse.ArgumentParser: Configured parser with ``dem-sim`` and
        ``ml-pipeline`` subparsers (``args.command`` selects between them).
    """
    parser = argparse.ArgumentParser(
        prog="bppm-dem-sm",
        description=(
            "Bidisperse DEM surrogate-model toolkit: launch a DEM "
            "simulation, or run the RNN surrogate experiment pipeline."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    dem_parser = subparsers.add_parser(
        "dem-sim",
        help="Launch a DEM simulation as a subprocess (YADE implemented; BlazeDEM not yet).",
        description="Launch a DEM simulation as a subprocess. --dem-backend yade requires YADE installed and on PATH.",
    )
    _add_dem_sim_arguments(dem_parser)

    ml_parser = subparsers.add_parser(
        "ml-pipeline",
        help="Run the experiment pipeline (simulate / process / train / predict / metrics / visualization).",
        description=(
            "Run the experiment pipeline (simulate / process / train / predict / "
            "metrics / visualization). Pass --config path.json to load settings from "
            "JSON; when set, other pipeline flags are ignored."
        ),
    )
    _add_ml_pipeline_arguments(ml_parser)

    return parser


def config_from_args(args: argparse.Namespace) -> ExperimentConfig:
    """Resolve ``ExperimentConfig`` from parsed ``ml-pipeline`` CLI args.

    If ``args.config`` is set, load only from that JSON file; all other
    pipeline flags are ignored. Otherwise apply any non-``None`` flags via
    :meth:`~bppm_dem_sm.config.ExperimentConfig.with_overrides` (flat leaf names).

    Args:
        args: Namespace produced by parsing the ``ml-pipeline`` subcommand.

    Returns:
        ExperimentConfig: Defaults with any non-``None`` CLI overrides
        applied, or the JSON-loaded config when ``--config`` is present.
    """
    if args.config is not None:
        return ExperimentConfig.from_json(args.config)

    overrides: dict[str, Any] = {}
    for name in _leaf_override_names():
        value = getattr(args, name, None)
        if value is not None:
            overrides[name] = value
    return ExperimentConfig().with_overrides(**overrides) if overrides else ExperimentConfig()


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI args, dispatch to the selected subcommand, return process exit code.

    Args:
        argv: Optional argument list (as for ``ArgumentParser.parse_args``);
            ``None`` uses ``sys.argv``.

    Returns:
        int: ``0`` on success; a nonzero exit code on failure (e.g. YADE not
        found, an unimplemented DEM backend, or the DEM subprocess itself
        exiting nonzero).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "dem-sim":
        return _run_dem_sim(args)
    return _run_ml_pipeline(args)


# --- Private helper functions ------------------------------------------------


def _bool_fields(cls: type) -> frozenset[str]:
    """Return the names of ``cls``'s fields annotated as ``bool``."""
    return frozenset(name for name, hint in get_type_hints(cls).items() if hint is bool)


def _path_fields(cls: type) -> frozenset[str]:
    """Return the names of ``cls``'s fields annotated as ``Path``."""
    return frozenset(name for name, hint in get_type_hints(cls).items() if hint is Path)


def _add_config_flag(container: Any, f, owning_cls: type) -> None:
    """Add one typed flag for a dataclass field; dest is the leaf field name."""
    flag = f"--{f.name.replace('_', '-')}"
    hint = get_type_hints(owning_cls)[f.name]
    default_repr = f.default
    if f.name in _bool_fields(owning_cls):
        container.add_argument(
            flag,
            action=argparse.BooleanOptionalAction,
            default=None,
            help=f"Override {f.name} (default: {default_repr}).",
        )
    elif f.name in _path_fields(owning_cls):
        container.add_argument(
            flag,
            type=Path,
            default=None,
            help=f"Override {f.name} (default: {default_repr}).",
        )
    elif hint is int:
        container.add_argument(
            flag,
            type=int,
            default=None,
            help=f"Override {f.name} (default: {default_repr}).",
        )
    elif hint is float:
        container.add_argument(
            flag,
            type=float,
            default=None,
            help=f"Override {f.name} (default: {default_repr}).",
        )
    else:
        container.add_argument(
            flag,
            type=str,
            default=None,
            help=f"Override {f.name} (default: {default_repr}).",
        )


def _add_ml_pipeline_arguments(parser: argparse.ArgumentParser) -> None:
    """Add all ``ExperimentConfig`` flags (plus ``--config``) to the ``ml-pipeline`` subparser.

    Emits one flag per core ``ExperimentConfig`` field and per nested options
    leaf (except ``feature_cols``, which uses ``--feature-cols``). Help text
    is grouped to match the nested JSON layout; flag names stay independent
    (``--epochs``, not ``--training-epochs``). This is also where
    ``--dem-backend``, ``--do-simulate``, and ``--do-process`` come from --
    they're plain ``ExperimentConfig`` fields like any other, so no extra
    wiring is needed here beyond this generic loop.
    """
    parser.add_argument(
        "--config",
        type=Path,
        metavar="JSON",
        help=(
            "JSON file with ExperimentConfig fields (nested option groups). "
            "When provided, all other pipeline config arguments are ignored."
        ),
    )

    core = parser.add_argument_group("pipeline")
    group_types = _option_group_types()
    for f in fields(ExperimentConfig):
        if f.name in _SKIP_CLI_FIELDS or f.name in group_types:
            continue
        _add_config_flag(core, f, ExperimentConfig)

    core.add_argument(
        "--feature-cols",
        nargs="+",
        default=None,
        metavar="COL",
        dest="feature_cols",
        help="Override feature_cols (space-separated column names).",
    )

    for group_name, group_cls in group_types.items():
        arg_group = parser.add_argument_group(group_name)
        for sf in fields(group_cls):
            _add_config_flag(arg_group, sf, group_cls)


def _add_dem_sim_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the ``dem-sim`` subcommand's flags (backend + script + executable)."""
    parser.add_argument(
        "--dem-backend",
        choices=DEM_BACKENDS,
        default="yade",
        dest="dem_backend",
        help="DEM backend to launch (default: 'yade'; 'blaze' not yet implemented).",
    )
    parser.add_argument(
        "--script",
        type=Path,
        default=None,
        metavar="PATH",
        help="DEM script to run (default: the packaged run_simulation.py for --dem-backend).",
    )
    parser.add_argument(
        "--yade-executable",
        type=str,
        default="yade",
        metavar="NAME",
        help="YADE executable name or path to look up on PATH (default: 'yade').",
    )


def _leaf_override_names() -> list[str]:
    """Return the CLI dest names that map onto ``ExperimentConfig.with_overrides``."""
    names = []
    group_types = _option_group_types()
    for f in fields(ExperimentConfig):
        if f.name in group_types:
            continue
        names.append(f.name)
    for group_cls in group_types.values():
        names.extend(sf.name for sf in fields(group_cls))
    return names


def _run_dem_sim(args: argparse.Namespace) -> int:
    """Handle the ``dem-sim`` subcommand: launch the DEM backend, return its exit code."""
    try:
        result = launcher.launch_simulation(
            script=args.script,
            yade_executable=args.yade_executable,
            backend=args.dem_backend,
        )
    except (FileNotFoundError, NotImplementedError) as exc:
        print(str(exc))
        return 1
    return result.returncode


def _run_ml_pipeline(args: argparse.Namespace) -> int:
    """Handle the ``ml-pipeline`` subcommand: resolve config and run the pipeline."""
    from .tf_quiet import silence_tensorflow

    silence_tensorflow()
    config = config_from_args(args)
    run_experiment_pipeline(config)
    return 0


# --- Script entry point ------------------------------------------------------

if __name__ == "__main__":
    raise SystemExit(main())
