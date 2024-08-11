#! /usr/bin/env bash

set -o errexit -o pipefail -o nounset -o xtrace

this_file="$(realpath "$0")"
scriptdir="$(dirname "$this_file")"
cd "$scriptdir/.." 

# start the container
# "$scriptdir/build_and_run_in_docker.bash" --keepalive &

# build_is_finished () {
#   local TAINERS
#   TAINERS="$(docker ps -q)"
#   local COUNT
#   COUNT="$(echo "$TAINERS" | wc -l)"
#   test -lt "$COUNT" 1 && return 1
#   docker logs "$TAINERS" | rg "build phase complete" && return 0 || return 1
# }

# local COUNT; COUNT="$(docker ps -q | wc -l)"


# until build_is_finished
# do
#   sleep 1
#   echo -n "."
# done
#
CONTAINER_ID=$(docker ps --no-trunc -q|head -n1)

sudo perf record -e cycles --call-graph dwarf -F 99 --cgroup "system.slice/docker-$CONTAINER_ID.scope"


