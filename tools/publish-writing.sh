#!/bin/sh
# Publish the newest Substack posts from this Mac, for when the Writing workflow on GitHub can't
# reach the feed (Substack turns GitHub's machines away, and rss2json, the stand-in, sometimes
# fails too). From a home connection the feed answers directly.
#
#     ./tools/publish-writing.sh
#
# It works on main as GitHub has it, in a throwaway worktree, so whatever branch or unsaved work
# this checkout holds is left alone. It commits and pushes only if the posts changed.
set -eu
cd "$(dirname "$0")/.."

tmp=$(mktemp -d)
trap 'git worktree remove --force "$tmp" >/dev/null 2>&1 || true; rm -rf "$tmp"' EXIT

git fetch -q origin main
git worktree add -q --detach "$tmp" origin/main
python3 "$tmp/tools/make-writing.py"
if git -C "$tmp" diff --quiet; then
  exit 0
fi
git -C "$tmp" commit -qam "Writing: newest Substack posts on the home page"
git -C "$tmp" push -q origin HEAD:main
echo "pushed; guzh.uk shows it in a minute or two"
