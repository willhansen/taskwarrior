#! /usr/bin/env bash

ctest --test-dir build -j "$(nproc)" --output-on-failure ${1:+ -R ".*$1.*"}
