#! /usr/bin/env python3

import argparse
import os
import subprocess
from pprint import pprint

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
        help="Run tests after building. If STRING is present, only run tests containing STRING in their name",
    )
    # TODO: mutually exclusive with 'keepalive'
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Leave user in interactive bash shell in container afterwards",
    )
    parser.add_argument(
        "-k",
        "--keepalive",
        action="store_true",
        help="Keep the container alive and headless",
    )

    args = parser.parse_args()

    host_script_dir = os.path.dirname(os.path.abspath(__file__))
    container_code_dir="/root/code"
    container_script_dir=f"{container_code_dir}/local-docker"

    entry_cmds = [
        f"{container_script_dir}/{file}"
        for file in ["build.bash", "build_tests.bash", "init.bash"]
    ] + ["echo 'build phase complete'"]

    if args.test:
        entry_cmds.append(f"{container_script_dir}/run_tests.bash")
        # TODO: test substring

    pprint(args.__dict__)
    print()
    if args.interactive:
        entry_cmds.append("bash")
    elif args.keepalive:
        entry_cmds.append("sleep infinity")

    pprint(entry_cmds)
    print()
    entry_cmds_final = sum([[x, "&&"] for x in entry_cmds], [])[:-1]
    pprint(entry_cmds_final)
    print()
    entry_cmd_final = " ".join(entry_cmds_final)

    os.chdir(f"{host_script_dir}/..")
    os.makedirs("build", exist_ok=True)
    os.makedirs("cargo-registry", exist_ok=True)

    code_dir = "/root/code"
    dockerfile = "./local-docker/dockerfile"
    image_tag = "image-for-local-taskwarrior-dev"

    subprocess.run(
        ["docker", "build", "-t", image_tag, "--file", dockerfile, "."], check=True
    )

    docker_run_args = [
        "--rm",
        f"--workdir={code_dir}",
        "--mount",
        f"type=bind,source=./build,destination={code_dir}/build",
        "--mount",
        f"type=bind,source=./cargo-registry,destination={code_dir}/../.cargo/registry",
    ]
    if args.interactive:
        docker_run_args.append("-it")
    docker_run_args += [
        image_tag,
        "bash",
        "-c",
        entry_cmd_final,
    ]

    cmd = ["docker", "run"] + docker_run_args
    print("=== Run Cmd ===")
    pprint(cmd)
    print()
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
