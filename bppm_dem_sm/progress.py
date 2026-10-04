"""Shared tqdm progress bars and stage banners for CLI pipeline runs."""

from __future__ import annotations

from tqdm import tqdm

# --- Constants ---------------------------------------------------------------

_RULE = "=" * 60


# --- Public functions --------------------------------------------------------


def plan(titles: list[str]) -> None:
    """Print which pipeline stages will run, in order.

    Args:
        titles: Display names of enabled stages, in execution order.
    """
    print(f"\n{_RULE}")
    print("  bppm-dem-sm ml-pipeline")
    if titles:
        print("  Stages: " + " -> ".join(titles))
    else:
        print("  Stages: (none enabled)")
    print(_RULE)


def stage(index: int, total: int, title: str) -> None:
    """Print a high-visibility banner for a pipeline stage.

    Args:
        index: 1-based index among enabled stages.
        total: Number of enabled stages.
        title: Stage display name.
    """
    print(f"\n{_RULE}")
    print(f"  STAGE {index}/{total}: {title}")
    print(_RULE)


def complete(message: str = "Pipeline complete.") -> None:
    """Print a closing banner after all stages finish.

    Args:
        message: Final status line shown inside the banner.
    """
    print(f"\n{_RULE}")
    print(f"  {message}")
    print(_RULE)


def track(iterable, desc: str, unit: str = "it", **kwargs):
    """Wrap ``iterable`` in a tqdm bar (same style as prediction).

    Args:
        iterable: Sequence or iterator to consume with a progress bar.
        desc: Left-side bar label.
        unit: Unit name shown on the right (e.g. ``frame``).
        **kwargs: Extra :class:`tqdm.tqdm` options.

    Returns:
        tqdm.tqdm: Progress-wrapped iterable.
    """
    return tqdm(iterable, desc=desc, unit=unit, dynamic_ncols=True, **kwargs)


def bar(total=None, desc: str = "", unit: str = "it", **kwargs):
    """Create a manual tqdm bar for callbacks that are not iterables.

    Args:
        total: Expected number of updates, or ``None`` if unknown.
        desc: Left-side bar label.
        unit: Unit name shown on the right (e.g. ``frame``).
        **kwargs: Extra :class:`tqdm.tqdm` options.

    Returns:
        tqdm.tqdm: Progress bar updated via ``update`` / ``n``.
    """
    return tqdm(total=total, desc=desc, unit=unit, dynamic_ncols=True, **kwargs)
