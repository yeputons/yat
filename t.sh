#!/bin/bash

set -e
set -u
source ./tlib.sh

download model.py

tst "smoke tests" ./run_smoke_tests.py

tdir=tests/eval
for prog in $tdir/*.y; do
  t=$tdir/$(basename $prog .y)
  checker=diff
  if [[ -f "$t.chk" ]]; then
    checker=$t.chk
  fi

  function go() {
    ./run.py $prog <$t.in >student.out && $checker $t.out student.out
  }
  tst "$t" go
  rm student.out
done

validate
