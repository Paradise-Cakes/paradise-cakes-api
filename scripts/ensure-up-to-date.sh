#!/bin/bash

set -eu

commit=$(git log -1 --format='%H')
if ! git merge-base --is-ancestor origin/main $commit ; then
  echo "This commit ${commit} is not up to date with main"
  exit 1
fi