#! /usr/bin/env bash

CODE_DIR="/root/code"

function print_help() {
  echo "Usage: $(basename "$0") [-h|--help] [-t|--test [STRING]]"
  echo ""
  echo "Options:"
  echo "  -h, --help            Show this help text"
  echo "  -t, --test [STRING]   Run tests after building"
  echo "                        If STRING is present, only run tests containing STRING in their name"
  echo "  -i, --interactive     Leave user in bash shell in container afterwards"
  echo ""
}

DO_TESTS=false
DO_END_IN_BASH=false
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
}
# print_args; exit 0


CMD_BUILD_TW="\
  cmake -S . -B build -DCMAKE_BUILD_TYPE=Release . && \
  cmake --build build -j $(nproc) \
  "
CMD_BUILD_TESTS="\
  cmake --build build -j $(nproc) --target build_tests \
  "

CMD_RUN_TESTS="\
  ctest --test-dir build -j $(nproc) --output-on-failure \
  "

CMD_INIT_TW="\
    ln -s /root/code/build/src/task /usr/local/bin/task && \
    ( echo 'yes' | task ) || true \
    "

COMBINED_CMD="\
    $CMD_BUILD_TW && \
    $CMD_BUILD_TESTS && \
    $CMD_INIT_TW \
  "


if [[ $DO_TESTS == true ]]; then
  if [[ "$TEST_SUBSTRING" != "" ]]; then
    # Select test by substring
    CMD_RUN_TESTS+=' -R .*'"$TEST_SUBSTRING"'.*'
  fi
  COMBINED_CMD+=" && $CMD_RUN_TESTS"
fi

if [[ $DO_END_IN_BASH == true ]]; then
  COMBINED_CMD+=" && bash"
fi



mkdir -p build && \
docker build \
-t foo \
--file ./docker/task.dockerfile . && \
  docker run \
    --rm \
    -it \
    --workdir "${CODE_DIR}" \
    --mount type=bind,source=./build,destination="${CODE_DIR}"/build \
    foo \
    bash -c "$COMBINED_CMD"
