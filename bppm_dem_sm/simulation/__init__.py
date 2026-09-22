"""YADE-only DEM simulation: mill setup, materials, ingress, and rotation.

Everything here runs inside YADE's embedded Python interpreter (``simulation``,
``sim_functions``) or shells out to it (``launcher``); nothing in this
subpackage is importable from the plain TensorFlow/pandas venv side except
``launcher``, which never imports yade itself.
"""
