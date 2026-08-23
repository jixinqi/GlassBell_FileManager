#!/usr/bin/env python3

import os
import pathlib
import subprocess
import datetime
import threading

from .environment_base import BuildType as BuildType
from .environment_base import LinkType  as LinkType
from .environment_base import environment_base as base

class environment_win(base):
    def __init__(self, *, build_type:BuildType, link_type:LinkType):
        super().__init__(
            build_type=build_type,
            link_type=link_type,
            output_dir_name="__output_windows"
        )
        self.__update_vcvarsall_env()

    def __update_vcvarsall_env(self):
        process_vswhere = subprocess.run(
            [
                "%ProgramFiles(x86)%/Microsoft Visual Studio/Installer/vswhere.exe",
                "-latest",
                "-products", "*",
                "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                "-property", "installationPath"
            ],
            shell=True,
            capture_output = True,
            text = True
        )
        process_vswhere_stdout_buffer = process_vswhere.stdout
        
        vs_install_dir          = pathlib.Path(process_vswhere_stdout_buffer.strip())
        vcvars64_bat_dir_path   = vs_install_dir / "VC" / "Auxiliary" / "Build"
        cmake_dir_path          = vs_install_dir / "Common7" / "IDE" / "CommonExtensions" / "Microsoft" / "CMake" / "CMake" / "bin"
        ninja_dir_path          = vs_install_dir / "Common7" / "IDE" / "CommonExtensions" / "Microsoft" / "CMake" / "Ninja"

        self.__env = os.environ.copy()
        self.__env["PATH"] = f"{self.__env['PATH']};{vcvars64_bat_dir_path.as_posix()};{cmake_dir_path.as_posix()};{ninja_dir_path.as_posix()};"

    def run_commands(self, commands:list[str], cwd:pathlib.Path, log_file:pathlib.Path):
        if(not log_file.parent.exists()):
            log_file.parent.mkdir(parents=True)

        with open(log_file, "w") as log_output_file:

            for command in commands:
                full_command = f"vcvars64.bat && {command}"

                command_header = ""
                command_header += ("=" * 80 + "\n")
                command_header += (str(datetime.datetime.now()) + "\n")
                command_header += (f"pwd: {cwd}" + "\n")
                command_header += (full_command + "\n")
                command_header += ("=" * 80 + "\n")
                
                self.mutex.acquire()
                print(command_header)
                self.mutex.release()

                log_output_file.write(command_header)
                log_output_file.flush()

                subprocess.run(
                    full_command,
                    shell=True,
                    env=self.__env,
                    cwd=cwd,
                    stdout=log_output_file,
                    stderr=log_output_file
                )

if(__name__ == "__main__"):
    os._exit(1)
