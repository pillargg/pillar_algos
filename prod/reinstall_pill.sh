#!/bin/bash

echo  "=============="
echo  "This will uninstall, build, install local pillaralgos"
echo  "=============="
pip uninstall pillaralgos
poetry build
pip install dist/*.whl
