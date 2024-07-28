#! /usr/bin/env bash

set -o errexit -o pipefail -o nounset -o xtrace

CODE_DIR="/root/code"
SCRIPT_DIR="$CODE_DIR/local-docker"
DOCKERFILE="./local-docker/dockerfile"
IMAGE_TAG="image-for-local-taskwarrior-dev"


function print_help() {
  echo "Usage:"
  echo ""
  echo "    ./local-docker/$(basename "$0") [-h|--help] [-t|--test [STRING]]"
  echo ""
  echo "Options:"
  echo "  -h, --help            Show this help text"
  echo "  -t, --test [STRING]   Run tests after building"
  echo "                        If STRING is present, only run tests containing STRING in their name"
  echo "  -i, --interactive     Leave user in bash shell in container afterwards"
  echo "  -k, --keepalive       Keep the container alive and headless" 
  echo ""
}

DO_TESTS=false
DO_END_IN_BASH=false
DO_KEEP_ALIVE=false
TEST_SUBSTRING=""
while test $# -gt 0; do
  case "$1" in
    -h | --help)
      print_help
      exit 0
      ;;
    -t | --test)
      DO_TESTS=true
      # With this approach, can't pass in arguments starting with a dash, like "-thing"
      if [[ "$2" =~ ^[^-].* ]]; then
        TEST_SUBSTRING="$2"
        shift
      fi
      shift
      ;;
    -i | --interactive)
      DO_END_IN_BASH=true
      shift
      ;;
    -k | --keepalive)
      DO_KEEP_ALIVE=true
      shift
      ;;
    -*)
      echo "Unknown option: $1"
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

#for debug
function print_args() {
  echo "DO_TESTS: $DO_TESTS"
  echo "TEST_SUBSTRING: $TEST_SUBSTRING"
  echo "DO_END_IN_BASH: $DO_END_IN_BASH"
  echo "DO_KEEP_ALIVE: $DO_KEEP_ALIVE"
}
print_args


ENTRY_CMD="\
  \"$SCRIPT_DIR/build.bash\" && \
  \"$SCRIPT_DIR/build_tests.bash\" && \
  \"$SCRIPT_DIR/init.bash\" && \
  echo 'build phase complete' && \
  true"


if [[ $DO_TESTS == true ]]; then
  ENTRY_CMD+=" && \"$SCRIPT_DIR/run_tests.bash\""
  if [[ "$TEST_SUBSTRING" != "" ]]; then
    # Select test by substring
    ENTRY_CMD+=" \"$TEST_SUBSTRING\""
  fi
fi

if [[ $DO_END_IN_BASH == true ]]; then
  ENTRY_CMD+=" && bash"
elif [[ $DO_KEEP_ALIVE == true ]]; then
  ENTRY_CMD+=" && sleep infinity"
fi


mkdir -p build
mkdir -p cargo-registry

docker build \
-t "$IMAGE_TAG" \
--file "$DOCKERFILE" .
docker run \
  --rm \
  -it \
  --workdir "${CODE_DIR}" \
  --mount type=bind,source=./build,destination="${CODE_DIR}"/build \
  --mount type=bind,source=./cargo-registry,destination="${CODE_DIR}"/../.cargo/registry \
  "$IMAGE_TAG" \
  bash -c "$ENTRY_CMD"
