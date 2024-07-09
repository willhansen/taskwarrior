#! /usr/bin/env bash

ln -s /root/code/build/src/task /usr/local/bin/task && \
  ( ( echo 'yes' | task ) || true ) 
