#!/bin/bash

set -e
set -u
source "./tlib.sh"

download model.py
download printer.py

for prog in tests/format/*.y; do
  echo "===== New test ====="
  function go() {
    cat $prog
    echo "====="
    ./format.py $prog >student.y || return 1
    ./parse.py student.y || return 1
    cat student.y
    echo -n "    Good or bad (g/b)? "
    read ans
    [[ "$ans" == "g" ]]
  }
  tst "$prog" go
  rm student.y
done

validate
