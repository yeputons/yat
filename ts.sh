#!/bin/bash

set -e
set -u
source "./tlib.sh"

download model.py
download static_analyzer.py
sed -i "s/from model/from yat.model/g" -i yat/static_analyzer.py
sed -i "s/import model/import yat.model/g" -i yat/static_analyzer.py

./test_static_analyze.py
