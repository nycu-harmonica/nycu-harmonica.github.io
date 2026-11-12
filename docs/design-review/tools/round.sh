#!/usr/bin/env bash
# One hill-climb round: build the worktree, photograph it, assemble the blind set.
#   docs/design-review/tools/round.sh N
set -euo pipefail
n=$1
here=$(cd "$(dirname "$0")" && pwd)
repo=$(git -C "$here" rev-parse --show-toplevel)
"$here/build.sh" new "$repo" 8412
rm -rf "/tmp/bmhc-review/sets/r$n"
nice node "$here/capture.mjs" site http://127.0.0.1:8412 "/tmp/bmhc-review/sets/r$n" 2>&1 | grep -v '^/tmp' || true
count=$(ls "/tmp/bmhc-review/sets/r$n" | wc -l)
expected=$(ls /tmp/bmhc-review/sets/baseline | wc -l)
echo "captured $count / $expected"
[[ $count == "$expected" ]]
python3 "$here/make_round.py" "$n" "/tmp/bmhc-review/sets/r$n"
