#! /usr/bin/env bash

ln -s /tmp/code/build/src/task /usr/local/bin/task && \
  ( ( echo 'yes' | task ) || true ) 
