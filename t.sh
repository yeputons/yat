#!/bin/bash

set -e
set -u

if [[ "$#" -ge 1 ]]; then
  function download() {
    URL=$(echo "$1" | sed "s~/blob/~/raw/~")

    if ! echo "$URL" | grep "\.py$"; then
      return 1
    fi

    wget "$URL" -O yat/model.py
  }
  download "$1" || download "$1/blob/master/model.py" || (echo "Unable to download file" && exit 1)
fi

fail=0

echo "Running PEP8..."
pep8 yat/model.py && echo "    ok" || fail=1

echo "Running smoke tests..."
./run_smoke_tests.py && echo "    ok" || fail=1

tdir=tests/eval
for prog in $tdir/*.y; do
  t=$tdir/$(basename $prog .y)
  echo "Running $t..."
  if ! ./run.py $prog <$t.in >student.out; then
    fail=1
  else
    checker=diff
    if [[ -f "$t.chk" ]]; then
      checker=$t.chk
    fi
    $checker $t.out student.out && echo "    ok" || fail=1
  fi
  rm student.out
done

if [[ "$fail" == "0" ]]; then
  echo -e "\e[32;1mPASS\e[0m"
else
  echo -e "\e[31;1mFAIL\e[0m"
fi
exit "$fail"
