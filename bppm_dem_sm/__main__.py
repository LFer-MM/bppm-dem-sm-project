"""Allow ``python -m bppm_dem_sm`` to run the ``bppm-dem-sm`` CLI (dem-sim / ml-pipeline)."""

from .tf_quiet import silence_tensorflow

silence_tensorflow()

from .cli import main

raise SystemExit(main())
