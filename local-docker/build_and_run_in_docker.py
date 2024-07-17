#! /usr/bin/env python3

import argparse
import os
import sys

EXIT_FAILURE = 1
EXIT_SUCCESS = 0


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Testing convenience script for taskwarrior",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # TODO: test substring
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Run tests after building\nIf STRING is present, only run tests containing STRING in their name",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Leave user in bash shell in container afterwards",
    )
    parser.add_argument(
        "-k",
        "--keepalive",
        action="store_true",
        help="Keep the container alive and headless",
    )

    args = parser.parse_args()

    script_directory = os.path.dirname(os.path.abspath(__file__))

    entry_cmds = [
        f"{script_directory}/{file}"
        for file in ["build.bash", "build_tests.bash", "init.bash"]
    ] + ["echo 'build phase complete'"]

    if args.test:
        entry_cmds.append(f"{script_directory}/run_tests.bash")
        # TODO: test substring

    if args.interactive:
        entry_cmds.append("bash")
    elif args.keepalive:
        entry_cmds.append("sleep infinity")

    entry_cmd_final = sum([[x,"&&"] for x in entry_cmds])[:-1]

    os.chdir(f"{script_directory}/..")
    os.mkdirs("build", exist_ok=True)
    os.mkdirs("cargo-registry", exist_ok=True)

    code_dir = "/root/code"
    dockerfile = "./local-docker/dockerfile"
    image_tag = "image-for-local-taskwarrior-dev"

    docker_args = [
        "--rm",
        f"--workdir {code_dir}",
        f"--mount type=bind,source=./build,destination={code_dir}/build",
        f"--mount type=bind,source=./cargo-registry,destination={code_dir}/../.cargo/registry",
    ]
    if args.interactive:
        docker_args.append("-it")


    cmd = ["docker", "run"] + docker_args + 
    subprocess.run()
