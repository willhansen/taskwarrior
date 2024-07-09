#! /usr/bin/env bash

cmake --build build -j "$(nproc)" --target build_tests
