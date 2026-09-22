"""Command-line interface for the bidisperse DEM surrogate-model toolkit.

Two subcommands, matching the project's two runtimes:

- ``dem-sim``: launches a YADE DEM simulation as a subprocess (requires YADE
  installed and on PATH; never imports yade itself -- see
  :mod:`bppm_dem_sm.simulation.launcher`).
- ``ml-pipeline``: runs the RNN surrogate pipeline (train / predict / metrics
  / visualization). Config can be supplied either as individual flags or as a
  JSON file via ``--config``. When ``--config`` is set, all other pipeline
  config flags are ignored. Flags stay flat (``--epochs``); they are mapped
  onto nested option groups on :class:`~bppm_dem_sm.config.PipelineConfig`.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import fields
from pathlib import Path
from typing import Any, get_type_hints

from .config import PipelineConfig, _option_group_types
from .pipeline import run_pipeline
from .simulation import launcher

_SKIP_CLI_FIELDS = frozenset({"feature_cols"})


def _bool_fields(cls: type) -> frozenset[str]:
    return frozenset(name for name, hint in get_type_hints(cls).items() if hint is bool)


def _path_fields(cls: type) -> frozenset[str]:
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
    """Add all ``PipelineConfig`` flags (plus ``--config``) to the ``ml-pipeline`` subparser.

    Emits one flag per core ``PipelineConfig`` field and per nested options
    leaf (except ``feature_cols``, which uses ``--feature-cols``). Help text
    is grouped to match the nested JSON layout; flag names stay independent
    (``--epochs``, not ``--training-epochs``).
    """
    parser.add_argument(
        "--config",
        type=Path,
        metavar="JSON",
        help=(
            "JSON file with PipelineConfig fields (nested option groups). "
            "When provided, all other pipeline config arguments are ignored."
        ),
    )

    core = parser.add_argument_group("pipeline")
    group_types = _option_group_types()
    for f in fields(PipelineConfig):
        if f.name in _SKIP_CLI_FIELDS or f.name in group_types:
            continue
        _add_config_flag(core, f, PipelineConfig)

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
    """Add the ``dem-sim`` subcommand's flags (YADE script + executable)."""
    parser.add_argument(
        "--script",
        type=Path,
        default=None,
        metavar="PATH",
        help=f"YADE script to run (default: packaged {launcher.DEFAULT_SIMULATION_SCRIPT}).",
    )
    parser.add_argument(
        "--yade-executable",
        type=str,
        default="yade",
        metavar="NAME",
        help="YADE executable name or path to look up on PATH (default: 'yade').",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level ``bppm-dem-sm`` parser with its two subcommands.

    Returns:
        argparse.ArgumentParser: Configured parser with ``dem-sim`` and
        ``ml-pipeline`` subparsers (``args.command`` selects between them).
    """
    parser = argparse.ArgumentParser(
        prog="bppm-dem-sm",
        description=(
            "Bidisperse DEM surrogate-model toolkit: launch a YADE DEM "
            "simulation, or run the RNN surrogate ML pipeline."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    dem_parser = subparsers.add_parser(
        "dem-sim",
        help="Launch a YADE DEM simulation as a subprocess (requires YADE on PATH).",
        description="Launch a YADE DEM simulation as a subprocess. Requires YADE installed and on PATH.",
    )
    _add_dem_sim_arguments(dem_parser)

    ml_parser = subparsers.add_parser(
        "ml-pipeline",
        help="Run the RNN surrogate pipeline (train / predict / metrics / visualization).",
        description=(
            "Run the RNN surrogate pipeline (train / predict / metrics / "
            "visualization). Pass --config path.json to load settings from "
            "JSON; when set, other pipeline flags are ignored."
        ),
    )
    _add_ml_pipeline_arguments(ml_parser)

    return parser


def _leaf_override_names() -> list[str]:
    """CLI dest names that map onto ``PipelineConfig.with_overrides``."""
    names = []
    group_types = _option_group_types()
    for f in fields(PipelineConfig):
        if f.name in group_types:
            continue
        names.append(f.name)
    for group_cls in group_types.values():
        names.extend(sf.name for sf in fields(group_cls))
    return names


def config_from_args(args: argparse.Namespace) -> PipelineConfig:
    """Resolve ``PipelineConfig`` from parsed ``ml-pipeline`` CLI args.

    If ``args.config`` is set, load only from that JSON file; all other
    pipeline flags are ignored. Otherwise apply any non-``None`` flags via
    :meth:`PipelineConfig.with_overrides` (flat leaf names).

    Args:
        args: Namespace produced by parsing the ``ml-pipeline`` subcommand.

    Returns:
        PipelineConfig: Defaults with any non-``None`` CLI overrides applied,
        or the JSON-loaded config when ``--config`` is present.
    """
    if args.config is not None:
        return PipelineConfig.from_json(args.config)

    overrides: dict[str, Any] = {}
    for name in _leaf_override_names():
        value = getattr(args, name, None)
        if value is not None:
            overrides[name] = value
    return PipelineConfig().with_overrides(**overrides) if overrides else PipelineConfig()


def _run_dem_sim(args: argparse.Namespace) -> int:
    """Handle the ``dem-sim`` subcommand: launch YADE, return its exit code."""
    try:
        result = launcher.launch_simulation(
            script=args.script, yade_executable=args.yade_executable
        )
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    return result.returncode


def _run_ml_pipeline(args: argparse.Namespace) -> int:
    """Handle the ``ml-pipeline`` subcommand: resolve config and run the pipeline."""
    from .tf_quiet import silence_tensorflow

    silence_tensorflow()
    config = config_from_args(args)
    run_pipeline(config)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI args, dispatch to the selected subcommand, return process exit code.

    Args:
        argv: Optional argument list (as for ``ArgumentParser.parse_args``);
            ``None`` uses ``sys.argv``.

    Returns:
        int: ``0`` on success; a nonzero exit code on failure (e.g. YADE not
        found, or the DEM subprocess itself exiting nonzero).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "dem-sim":
        return _run_dem_sim(args)
    return _run_ml_pipeline(args)


if __name__ == "__main__":
    raise SystemExit(main())
