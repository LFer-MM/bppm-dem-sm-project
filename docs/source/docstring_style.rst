Docstring and comment style
===========================

Every Python file in ``bppm_dem_sm/`` and ``tests/`` follows the conventions
below. They are what :doc:`api` is generated from (Sphinx ``autodoc`` +
``napoleon``), so following them is what keeps the API reference correct.
``ruff check`` enforces the docstring rules for the package (``D`` rules,
Google convention, plus ``D401`` imperative mood; see ``pyproject.toml``).

To check the rendered docs, build them in nitpicky mode; it should finish with
no warnings::

    sphinx-build -b html -n docs/source docs/build/html

Docstrings
----------

Google style, triple double quotes, lines no longer than 99 characters.

**Summary line.** One line, ending in a period. Functions and methods use the
imperative mood ("Compute ...", "Return ...", "Build ..."); classes,
properties, and modules use a noun phrase. A blank line separates the summary
from the body.

**Sections**, always in this order and only when they apply:

1. ``Args:`` -- every parameter, ``name: Description.`` Types live in the
   signature, not here. Continuation lines are indented four more spaces.
2. ``Attributes:`` -- public dataclass fields and other public attributes
   (classes only).
3. ``Returns:`` / ``Yields:`` -- ``type: Description.`` Leave the section out
   when the function returns ``None``.
4. ``Raises:`` -- each exception raised on purpose, ``ExcType: When.``
5. ``Note:`` / ``Warning:`` / ``Example:``.

Free-form paragraphs go between the summary and ``Args:``, never between
sections.

.. code-block:: python

   def lacey_index_for_frame(df, cell_size, tracer_radius, min_particles_per_cell=5):
       """Compute Lacey M on a 3D cell grid for one frame.

       Particles are binned into cubic cells of edge ``cell_size``. Cells with
       fewer than ``min_particles_per_cell`` are ignored.

       Args:
           df: Frame table with columns ``x``, ``y``, ``z``, ``r``.
           cell_size: Cubic cell edge length in meters.
           tracer_radius: Radius identifying the tracer (large) species.
           min_particles_per_cell: Minimum count for a cell to contribute.

       Returns:
           tuple: ``(M, n_cells_used, p_global, mean_particles_per_cell)``.
       """

**Type names** in ``Returns:``/``Yields:`` are fully qualified so they link to
upstream docs through intersphinx: ``numpy.ndarray``, ``pandas.DataFrame``,
``pathlib.Path``, ``matplotlib.figure.Figure``. Optional results are written
``X | None`` (matching the annotations), tuples as ``tuple`` or
``tuple[A, B]`` followed by a ``(a, b)`` description.

**Array shapes** are written as tuples: ``(T, N, 3)``.

**Units** are SI and stated with the quantity: "in meters", "(s)", "(m)".

**Cross-references.** Use Sphinx roles with the fully qualified path for
public objects, adding ``~`` to show only the last component:
``:func:`~bppm_dem_sm.metrics.lacey_mixing_index.extract_frame_index```.
Short names only resolve inside the same module. Private objects
(``_name``) are not rendered by autodoc, so refer to them as literals
(````_save_sphere_frame````) instead of with a role. Parameters, field
names, file names, and code also go in double backticks.

**Characters.** ASCII only: write ``->``, ``--``, and ``-`` rather than
arrows or Unicode dashes (the PDF build uses pdflatex).

**Content.** Docstrings describe what the code does now and why. History
("renamed from ...", "used to ...") belongs in commit messages.

Modules and packages
~~~~~~~~~~~~~~~~~~~~

Every ``.py`` file, including ``__init__.py`` and tests, starts with a module
docstring: a one-line summary, then optional paragraphs. Package
``__init__`` docstrings are rendered as section overviews in :doc:`api`.

Classes and dataclasses
~~~~~~~~~~~~~~~~~~~~~~~

Document constructor arguments in ``__init__``'s docstring (``Args:``);
``napoleon_include_init_with_doc`` merges it into the class entry. Dataclasses
list their public fields under ``Attributes:`` in the class docstring.
Properties are documented like attributes: a noun-phrase summary and no
``Returns:`` section.

Module-level constants
~~~~~~~~~~~~~~~~~~~~~~

Public constants get a ``#:`` comment on the line(s) directly above them, which
autodoc renders as the constant's documentation::

    #: Valid values for ``ExperimentConfig.dem_backend``.
    DEM_BACKENDS = ("yade", "blaze")

Do not put a colon in the first line of a ``#:`` comment: napoleon reads
``Text: more`` as ``type: description``. Private module state (``_name``)
uses a plain ``#`` comment.

Private helpers and nested functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Give them at least a one-line docstring. Use full sections when the helper is
non-trivial.

Comments
--------

- English, sentence case, one space after ``#``, two spaces before an inline
  comment.
- Explain why, units, or shapes (``# (N, seq_len, F)``, ``# rad/s``), not
  what the next line obviously does.
- Avoid commented-out code. When kept on purpose (e.g. manual YADE steps),
  put a comment above it saying how it is meant to be used.

File layout
-----------

Every file has the same shape: module docstring, then imports (sorted by
ruff), then the top-level code in a fixed order of sections. Empty sections
are left out.

Package files (``bppm_dem_sm/``, and non-test modules such as
``tests/helpers.py``):

1. ``Constants`` -- module-level values that never change.
2. ``Module state`` -- module-level variables mutated at run time (e.g.
   ``BALANCE_STATE``, ``MATERIALS_MAP``).
3. ``Public classes``
4. ``Public functions``
5. ``Private classes`` -- names starting with ``_``.
6. ``Private helper functions`` -- names starting with ``_``.
7. ``Script entry point`` -- the ``if __name__ == "__main__":`` block.

Test files (``test_*.py``):

1. ``Setup`` -- module-level constants.
2. ``Helpers`` -- helper functions and stub classes.
3. ``Tests`` -- ``test_*`` functions.

When a file has two or more sections, each one starts with a divider padded
with ``-`` to column 79, preceded by two blank lines (one when it directly
follows the imports, as ruff's import sorting requires). A divider may add a
qualifier after a colon to split one section into named groups, as
``config.py`` does::

    # --- Public functions --------------------------------------------------------

    # --- Constants: paths and dataset defaults -----------------------------------

A file with a single section (most small modules and tests) has no dividers.
Code stays in its own module; placing a helper at the bottom of its file
under ``Private helper functions`` instead of next to its caller is the
accepted trade-off for a predictable layout.

``tests/test_code_layout.py`` checks every file against these rules, so a
misplaced function or a non-standard divider fails the test suite. The only
exemption is ``bppm_dem_sm/__main__.py``, whose statements must run in order.

Tests
-----

- Every test module has a module docstring naming what it covers.
- ``test_*`` functions are named descriptively and need no docstring. Add one
  only when the scenario needs explaining.
- Helpers and stub classes get a one-line docstring. Stub methods that just
  mirror a real API (e.g. Keras ``fit``/``save``) do not need one.
- Helpers used by more than one test module live in ``tests/helpers.py``
  (imported as ``from helpers import ...``) instead of being copied.
