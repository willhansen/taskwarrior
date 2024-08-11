#! /usr/bin/env python3
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--loop", action="store_true")
parser.add_argument("-t", "--test-substring", action="store")
parser.add_argument("-E", "--exclude", action="store")
args = parser.parse_args()

print(args)

test_cores = int(subprocess.check_output("nproc")) - 2

cmd = "ctest --output-on-failure --test-dir build -j".split() + [
    str(test_cores),
]
if args.test_substring is not None:
    cmd += ["-R", f".*{args.test_substring}.*"]
if args.exclude is not None:
    cmd += ["-E", args.exclude]
while True:
    subprocess.run(cmd, check=True)
    if not args.loop:
        break
