#!/bin/bash

set -u
set -e

PARSED=($(./repo_parse.py "$@"))
FILES="model.py folder.py printer.py"
REPO_URL="${PARSED[0]}"
BRANCH="${PARSED[1]}"
SUBP="${PARSED[2]}"

echo Cleaning...
rm -rf repo >/dev/null 2>&1 || true
for f in $FILES; do rm yat/$f >/dev/null 2>&1 || true; done
echo "  Done"

BRANCH_ARG=""
if [ -n "$BRANCH" ]; then
  BRANCH_ARG="--branch=$BRANCH"
fi

echo git clone "$REPO_URL" repo --depth=1 "$BRANCH_ARG"
git clone "$REPO_URL" repo --depth=1 "$BRANCH_ARG"

fail=0
for f in $FILES; do
  echo "Looking for $f..."
  RES=$(find "repo/$SUBP" -name $f)
  CNT=$(echo "$RES" | wc -l)
  if [[ -z "$RES" || $CNT == 0 ]]; then
    echo "  Not found"
    fail=1
    continue
  elif [[ $CNT > 1 ]]; then
    echo "  More than one found"
    exit 1
  fi
  cp "$RES" "yat/$f"
  echo "  Done"
  echo "Running pycodestyle..."
  if pycodestyle "yat/$f"; then
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
