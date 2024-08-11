#! /usr/bin/env python3
import argparse, subprocess

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--loop", action="store_true")
parser.add_argument("-t", "--test-substring", action="store")
args = parser.parse_args()

print(args)

cmd = "ctest --output-on-failure --test-dir build -j".split() + [
    subprocess.check_output("nproc"),
]
if args.test_substring is not None:
    cmd += ["-R", f".*{args.test_substring}.*"]
while True:
    subprocess.run(cmd, check=True)
    if not args.loop:
        break

