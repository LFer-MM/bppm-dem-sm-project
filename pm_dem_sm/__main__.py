"""Allow ``python -m pm_dem_sm`` to run the ``pm-dem-sm`` CLI (dem-sim / ml-pipeline)."""

from .tf_quiet import silence_tensorflow

silence_tensorflow()

from .cli import main

raise SystemExit(main())
