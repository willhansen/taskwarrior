#! /usr/bin/env bash

thefile="$(realpath "$0")"
scriptdir="$(dirname "$thefile")"
cd "$scriptdir/.." || exit 1

# start the container
"$scriptdir/build_and_run_in_docker.bash" --keepalive &

build_is_finished () {
  local TAINERS
  TAINERS="$(docker ps -q)"
  local COUNT
  COUNT="$(echo "$TAINERS" | wc -l)"
  test -lt "$COUNT" 1 && return 1
  docker logs "$TAINERS" | rg "build phase complete" && return 0 || return 1
}

# local COUNT; COUNT="$(docker ps -q | wc -l)"


until build_is_finished
do
  sleep 1
  echo -n "."
done

