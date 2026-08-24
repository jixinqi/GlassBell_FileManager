#!/usr/bin/env python3

import sys
import pathlib
dependency_builder_dir = pathlib.Path(__file__).parent.parent
sys.path.append(str(dependency_builder_dir))

import environment as environment

if __package__ in (None, ""):
    from builder_base import builder_base
else:
    from .builder_base import builder_base

class builder_zlib(builder_base):
    def __init__(self, env:environment.base):
        super().__init__("zlib", env)

    def build_impl(self):
        build_shared = "ON" if self.env.link_type == environment.LinkType.SHARED else "OFF"
        build_static = "ON" if self.env.link_type == environment.LinkType.STATIC else "OFF"

        if(isinstance(self.env, environment.win)):
            cmake_platform_options = ' -DCMAKE_CXX_FLAGS_INIT="/utf-8"'
        elif(isinstance(self.env, environment.linux)):
            cmake_platform_options = ""
        else:
            raise RuntimeError(f"Unsupported environment: {type(self.env).__name__}")

        self.env.run_commands(
            commands = [
                f'cmake -B "{self.module_build_dir.as_posix()}"'
                    f' -S "{self.module_pre_build_dir.as_posix()}"'
                    f' -DCMAKE_INSTALL_PREFIX="{self.module_install_dir.as_posix()}"'
                    f' -DCMAKE_BUILD_TYPE={self.env.build_type.value}'

                    f'{cmake_platform_options}'

                    f' -DZLIB_BUILD_TESTING=OFF'
                    f' -DZLIB_BUILD_SHARED={build_shared}'
                    f' -DZLIB_BUILD_STATIC={build_static}'
                    ,
                f'cmake --build   "{self.module_build_dir.as_posix()}" --config={self.env.build_type.value} -j',
                f'cmake --install "{self.module_build_dir.as_posix()}" --config={self.env.build_type.value}',
            ],
            cwd = self.module_pre_build_dir,
            log_file = self.module_install_dir / f"build__{self.module_name}.log"
        )

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Build and install zlib")
    parser.add_argument("--build-type", choices=[build_type.value for build_type in environment.BuildType], required=True)
    parser.add_argument("--link-type", choices=[link_type.value for link_type in environment.LinkType], required=True)
    args = parser.parse_args()

    env = environment.current(
        build_type=environment.BuildType(args.build_type),
        link_type=environment.LinkType(args.link_type)
    )
    builder_zlib(env).build()

if(__name__ == "__main__"):
    main()
