#! /usr/bin/env python3

import argparse
import os
import subprocess
from pprint import pprint

EXIT_FAILURE = 1
EXIT_SUCCESS = 0

code_dir = "/tmp/code"


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
    # TODO: only valid when args.test is True
    parser.add_argument(
        "-w",
        "--wait",
        action="store_true",
        help="Wait for user input before running tests",
    )
    parser.add_argument(
        "-l",
        "--loop-tests",
        action="store_true",
        help="continually re-run the tests",
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
    parser.add_argument(
        "-E",
        "--exclude",
        action="store",
    )

    args = parser.parse_args()

    host_script_dir = os.path.dirname(os.path.abspath(__file__))
    container_code_dir = "/tmp/code"
    container_script_dir = f"{container_code_dir}/local-docker"

    entry_cmds = [
        f"{container_script_dir}/{file}"
        for file in ["build.bash", "build_tests.bash", "init.bash"]
    ]

    if args.test:
        if args.wait:
            entry_cmds.append(f"{container_script_dir}/wait_for_key.bash")
        entry_cmds.append(
            f"{container_script_dir}/run_tests.py"
            + (" --loop" if args.loop_tests else "")
            + (f" -E {args.exclude}" if args.exclude else "")
        )
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
    pprint(entry_cmd_final)
    print()

    os.chdir(f"{host_script_dir}/..")
    os.makedirs("build", exist_ok=True)
    os.makedirs("cargo-registry", exist_ok=True)

    code_dir = "/tmp/code"
    dockerfile = "./local-docker/dockerfile"
    image_tag = "image-for-local-taskwarrior-dev"

    docker_cmd = "podman"

    subprocess.run(
        [docker_cmd, "build", "-t", image_tag, "--file", dockerfile, "."], check=True
    )

    docker_run_args = [
        "--rm",
        f"--workdir={code_dir}",
        "--mount",
        f"type=bind,source=./build,destination={code_dir}/build",
        "--mount",
        f"type=bind,source=./cargo-registry,destination={code_dir}/../.cargo/registry",
        "-it",
    ]
    docker_run_args += [
        image_tag,
        "bash",
        "-c",
        # "pwd && ls && ls /tmp && ls /tmp/code && ls /tmp/code/local-docker"
        entry_cmd_final,
    ]

    cmd = [docker_cmd, "run"] + docker_run_args
    print("=== Run Cmd ===")
    pprint(cmd)
    print()
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
