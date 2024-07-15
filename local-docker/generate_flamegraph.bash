#! /usr/bin/env bash

cd "$(realpath "$0")/.." || exit 1
scriptdir="$(dirname "$0")"

# start the container
"$scriptdir/build_and_run_in_docker.bash" -i &

build_is_finished () {
  docker logs "$(docker ps -q)" | rg "build phase complete"
}

until build_is_finished
do
  sleep 1
  echo -n "."
done

