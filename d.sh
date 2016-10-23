#!/bin/bash

set -u
set -e

URL="$(echo "$1" | sed "s~/tree/master\(/.*\|$\)~~" | sed "s~\.git\$~~")"
SUBP="./"
if echo "$1" | grep "/tree/master"; then
  SUBP="./$(echo "$1" | sed "s~.*/tree/master\(\)~\1~")"
fi
FILES="model.py folder.py printer.py"

echo Cleaning...
rm -rf repo >/dev/null 2>&1 || true
for f in $FILES; do rm yat/$f >/dev/null 2>&1 || true; done
echo "  Done"

git clone "$URL" repo --depth=1

fail=0
for f in $FILES; do
  echo "Looking for $f..."
  RES=$(find "repo/$SUBP" -name $f)
  CNT=$(echo "$RES" | wc -l)
  if [[ $CNT == 0 ]]; then
    echo "  Not found"
    fail=1
  elif [[ $CNT > 1 ]]; then
    echo "  More than one found"
    exit 1
  fi
  mv "$RES" "yat/$f"
  echo "  Done"
  echo "Running PEP8..."
  if pep8 "yat/$f"; then
    echo "  Done"
  else
    fail=1
  fi
done
if [[ $fail == 0 ]]; then
  echo -e "\e[1;32mPASS\e[0m"
  rm -rf >/dev/null 2>&1 || true
else
  echo -e "\e[1;31mFAIL\e[0m"
fi
exit $fail
