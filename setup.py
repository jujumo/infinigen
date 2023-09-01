from pathlib import Path
import subprocess
import sys
import os

from setuptools import setup, find_packages, Extension

import numpy
from Cython.Build import cythonize

cwd = Path(__file__).parent

def ensure_submodules():
    # Inspired by https://github.com/pytorch/pytorch/blob/main/setup.py

    with (cwd/'.gitmodules').open() as f:
        submodule_folders = [
            cwd/line.split("=", 1)[1].strip()
            for line in f.readlines()
            if line.strip().startswith("path")
        ]

    if any(not p.exists() or not any(p.iterdir()) for p in submodule_folders):
        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"], cwd=cwd
        )    

ensure_submodules()

# inspired by https://github.com/pytorch/pytorch/blob/161ea463e690dcb91a30faacbf7d100b98524b6b/setup.py#L290
# theirs seems to not exclude dist_info but this causes duplicate compiling in my tests
dont_build_steps = ["clean", "egg_info", "dist_info", "sdist", "--help"]
RUN_BUILD = not any(x in sys.argv[1] for x in dont_build_steps) 
str_true = "True" # use strings as os.environ will turn any bool into a string anyway
if RUN_BUILD and os.environ.get('INFINIGEN_INSTALL_RUNBUILD', str_true) == str_true:
    if os.environ.get('INFINIGEN_INSTALL_TERRAIN', str_true) == str_true:
        subprocess.run(['make', 'terrain'], cwd=cwd)
    if os.environ.get('INFINIGEN_INSTALL_CUSTOMGT', str_true) == str_true:
        subprocess.run(['make', 'customgt'], cwd=cwd)

cython_extensions = []

cython_extensions.append(Extension(
    name="bnurbs",
    sources=["infinigen/assets/creatures/util/geometry/cpp_utils/bnurbs.pyx"],
    include_dirs=[numpy.get_include()]
))
cython_extensions.append(
    Extension(
        name="infinigen.terrain.marching_cubes",
        sources=["infinigen/terrain/marching_cubes/_marching_cubes_lewiner_cy.pyx"],
        include_dirs=[numpy.get_include()]
    )
)

setup(
    ext_modules=[
        *cythonize(cython_extensions)
    ]
    # other opts come from pyproject.toml
)
