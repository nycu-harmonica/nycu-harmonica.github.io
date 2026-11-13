#!/usr/bin/env bash
# Build one version of the site for screenshots and serve it on 127.0.0.1.
#   docs/design-review/tools/build.sh baseline origin/main 8411
#   docs/design-review/tools/build.sh new WORKTREE 8412
# A git ref is exported with `git archive` (no checkout is touched); a
# directory is built in place. Waits while load1 > 10 before building.
set -euo pipefail
name=$1 source=$2 port=$3
root=/tmp/bmhc-review
repo=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
while (( $(awk '{print int($1)}' /proc/loadavg) > 10 )); do echo "load $(cut -d' ' -f1 /proc/loadavg), waiting"; sleep 30; done
if [[ -d $source ]]; then src=$source; else
  src=$root/src/$name; rm -rf "$src"; mkdir -p "$src"
  git -C "$repo" archive "$source" | tar -x -C "$src"
fi
rm -rf "$root/build/$name"
nice hugo --gc --minify --quiet -s "$src" -d "$root/build/$name" --cacheDir "$root/hugo-cache"
pkill -f "http.server $port" 2>/dev/null || true
nohup python3 -m http.server "$port" --bind 127.0.0.1 -d "$root/build/$name" >/dev/null 2>&1 &
sleep 1
echo "serving $name at http://127.0.0.1:$port"
