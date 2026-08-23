#!/usr/bin/env python3

import datetime
import os
import pathlib
import subprocess

from .environment_base import BuildType as BuildType
from .environment_base import LinkType as LinkType
from .environment_base import environment_base as base

class environment_linux(base):
    def __init__(self, *, build_type:BuildType, link_type:LinkType):
        super().__init__(
            build_type=build_type,
            link_type=link_type,
            output_dir_name="__output_linux"
        )

    def run_commands(self, commands:list[str], cwd:pathlib.Path, log_file:pathlib.Path):
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, "w") as log_output_file:
            for command in commands:
                command_header = ""
                command_header += ("=" * 80 + "\n")
                command_header += (str(datetime.datetime.now()) + "\n")
                command_header += (f"pwd: {cwd}\n")
                command_header += (command + "\n")
                command_header += ("=" * 80 + "\n")

                with self.mutex:
                    print(command_header)

                log_output_file.write(command_header)
                log_output_file.flush()

                subprocess.run(
                    command,
                    shell=True,
                    executable="/bin/bash",
                    cwd=cwd,
                    stdout=log_output_file,
                    stderr=subprocess.STDOUT,
                    check=True
                )


if(__name__ == "__main__"):
    os._exit(1)
