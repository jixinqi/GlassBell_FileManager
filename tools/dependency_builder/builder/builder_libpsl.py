#!/usr/bin/env python3

import sys
import pathlib
dependency_builder_dir = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(dependency_builder_dir))

import shutil

import environment as environment

if __package__ in (None, ""):
    from builder_base import builder_base
else:
    from .builder_base import builder_base

class builder_libpsl(builder_base):
    def __init__(self, env:environment.base):
        super().__init__("libpsl", env)

    def __generate_suffixes_dafsa_h(self):
        python_executable = pathlib.Path(sys.executable).as_posix()
        self.env.run_commands(
            commands = [
                f'"{python_executable}" src/psl-make-dafsa --output-format=cxx+ list/public_suffix_list.dat suffixes_dafsa.h',
            ],
            cwd = self.module_pre_build_dir,
            log_file = self.module_install_dir / f"build__{self.module_name}.log"
        )

    def __generate_libpsl_h(self):
        psl_version        = ""
        psl_version_major  = ""
        psl_version_minor  = ""
        psl_version_patch  = ""
        psl_version_number = ""

        with open(self.module_pre_build_dir / "version.txt") as version_file:
            psl_version = version_file.read().strip()
            psl_version_major, psl_version_minor, psl_version_patch = psl_version.split(".")
            psl_version_number = f"0x{int(psl_version_major):02X}{int(psl_version_minor):02X}{int(psl_version_patch):02X}"

        libpsl_h_content = ""
        with open(self.module_pre_build_dir / "include" / "libpsl.h.in") as libpsl_h_in_file:
            libpsl_h_in_file_lines = libpsl_h_in_file.readlines()
            for line in libpsl_h_in_file_lines:
                line = line.replace("@LIBPSL_VERSION@",        f"{psl_version}")
                line = line.replace("@LIBPSL_VERSION_MAJOR@",  f"{psl_version_major}")
                line = line.replace("@LIBPSL_VERSION_MINOR@",  f"{psl_version_minor}")
                line = line.replace("@LIBPSL_VERSION_PATCH@",  f"{psl_version_patch}")
                line = line.replace("@LIBPSL_VERSION_NUMBER@", f"{psl_version_number}")
                libpsl_h_content += line

        with open(self.module_pre_build_dir / "include" / "libpsl.h", "w") as libpsl_h_file:
            libpsl_h_file.write(libpsl_h_content)

    def __generate_cmake_file(self):
        shutil.copy(
            pathlib.Path(__file__).parent / "build_spec" / "libpsl" / "CMakeLists.txt",
            self.module_pre_build_dir / "CMakeLists.txt"
        )

    def build_impl(self):
        build_shared = "ON" if self.env.link_type == environment.LinkType.SHARED else "OFF"

        if(isinstance(self.env, environment.win)):
            cmake_platform_options = ' -DCMAKE_CXX_FLAGS_INIT="/utf-8"'
        elif(isinstance(self.env, environment.linux)):
            cmake_platform_options = ""
        else:
            raise RuntimeError(f"Unsupported environment: {type(self.env).__name__}")

        self.__generate_suffixes_dafsa_h()
        self.__generate_libpsl_h()
        self.__generate_cmake_file()

        self.env.run_commands(
            commands = [
                f'cmake -B "{self.module_build_dir.as_posix()}"'
                    f' -S "{self.module_pre_build_dir.as_posix()}"'
                    f' -DCMAKE_INSTALL_PREFIX="{self.module_install_dir.as_posix()}"'
                    f' -DCMAKE_BUILD_TYPE={self.env.build_type.value}'

                    f'{cmake_platform_options}'
                    f' -DBUILD_SHARED_LIBS={build_shared}'
                    ,
                f'cmake --build   "{self.module_build_dir.as_posix()}" --config={self.env.build_type.value} -j',
                f'cmake --install "{self.module_build_dir.as_posix()}" --config={self.env.build_type.value}'
            ],
            cwd = self.module_pre_build_dir,
            log_file = self.module_install_dir / f"build__{self.module_name}.log"
        )

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Build and install libpsl")
    parser.add_argument("--build-type", choices=[build_type.value for build_type in environment.BuildType], required=True)
    parser.add_argument("--link-type", choices=[link_type.value for link_type in environment.LinkType], required=True)
    args = parser.parse_args()

    env = environment.current(
        build_type=environment.BuildType(args.build_type),
        link_type=environment.LinkType(args.link_type)
    )
    builder_libpsl(env).build()

if(__name__ == "__main__"):
    main()
