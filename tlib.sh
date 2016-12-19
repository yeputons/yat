set -e
set -u

t_fail=0
BASE_URL="${1:-}"

function download() {
  if [[ -n "$BASE_URL" ]]; then
    local URL=$(echo "$BASE_URL" | sed "s~[a-z_]\+\.py~$1~")

    if ! echo "$URL" | grep "$1"; then
      URL+="/blob/master/$1"
    fi

    local URL=$(echo "$URL" | sed "s~/blob/~/raw/~")

    echo "Downloading $1..."
    if ! wget "$URL" -O "yat/$1" >/dev/null 2>&1; then
      echo "Unable to download $1"
      exit 1
    fi
    echo "    ok"
  fi
  if ! [[ -e "yat/$1" ]]; then
    echo "File yat/$1 not found"
    exit 1
  fi
  echo "Running PEP8 on yat/$1..."
  pep8 "yat/$1" && echo "    ok" || t_fail=1
}

function tst() {
  echo "Running $1..."
  shift
  if "$@"; then
    echo "    ok"
  else
    t_fail=1
  fi
}

function validate() {
  if [[ "$t_fail" == "0" ]]; then
    echo -e "\e[32;1mPASS\e[0m"
  else
    echo -e "\e[31;1mFAIL\e[0m"
  fi
  exit "$t_fail"
}
