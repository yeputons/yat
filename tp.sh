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

    sed -i "s/\t/    /g" student.y
    indent=""
    for ((i=1; $i <= 10; i++)); do
      indent+=" "
      if grep "^$indent[^ ]" student.y >/dev/null 2>&1; then
        echo "Detected indent = |$indent|"
        sed -i "s/$indent/    /g" student.y
        break
      fi
    done
    unix2dos student.y >/dev/null 2>&1

    ./parse.py student.y || return 1
    diff -y $prog student.y
    echo -n "    Good or bad (g/b)? "
    read ans
    [[ "$ans" == "g" ]]
  }
  tst "$prog" go
  rm student.y
done

validate
