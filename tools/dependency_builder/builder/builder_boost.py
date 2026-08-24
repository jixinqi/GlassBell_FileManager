#!/usr/bin/env python3

import sys
import pathlib
dependency_builder_dir = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(dependency_builder_dir))

import environment as environment

if __package__ in (None, ""):
    from builder_base import builder_base
else:
    from .builder_base import builder_base

class builder_boost(builder_base):
    def __init__(self, env:environment.base):
        super().__init__("boost", env)

    def __write_user_config_jam(self):
        openssl_dir = self.env.install_dir / "openssl"
        user_config_file = self.module_build_dir / "user-config.jam"
        if(isinstance(self.env, environment.win)):
            with open(user_config_file, "w", encoding="utf-8", newline="\n") as output_file:
                output_file.write(
                    "using openssl : : "
                    f'"<include>{(openssl_dir / "include").as_posix()}" '
                    f'"<search>{(openssl_dir / "lib").as_posix()}" '
                    "<ssl-name>libssl <crypto-name>libcrypto ;\n"
                )
        elif(isinstance(self.env, environment.linux)):
            with open(user_config_file, "w", encoding="utf-8", newline="\n") as output_file:
                output_file.write(
                    "using openssl : : "
                    f'"<include>{(openssl_dir / "include").as_posix()}" '
                    f'"<search>{(openssl_dir / "lib64").as_posix()}" '
                    "<ssl-name>ssl <crypto-name>crypto ;\n"
                )
        else:
            raise RuntimeError(f"Unsupported environment: {type(self.env).__name__}")

        return user_config_file

    def build_impl(self):
        if(isinstance(self.env, environment.win)):
            bootstrap_cmd = "bootstrap.bat msvc"
            b2_executable = "b2"
        elif(isinstance(self.env, environment.linux)):
            bootstrap_cmd = "./bootstrap.sh --with-libraries=all --with-python=python3"
            b2_executable = "./b2"
        else:
            raise RuntimeError(f"Unsupported environment: {type(self.env).__name__}")

        variant = self.env.build_type.value.lower()
        link_type = self.env.link_type.value.lower()
        user_config_jam_file = self.__write_user_config_jam()
        b2_cmd = (
            f'{b2_executable} install address-model=64 -j4'
            f' --without-mpi'
            f' --without-graph_parallel'
            f' --build-dir="{self.module_build_dir.as_posix()}"'
            f' --prefix="{self.module_install_dir.as_posix()}"'
            f' --user-config="{user_config_jam_file.as_posix()}"'
            f' variant={variant}'
            f' link={link_type}'
            f' cxxstd=20'
        )
        if(isinstance(self.env, environment.win)):
            b2_cmd += f' runtime-link={link_type}'

        commands = [
            bootstrap_cmd,
            b2_cmd
        ]

        self.env.run_commands(
            commands = commands,
            cwd = self.module_pre_build_dir,
            log_file = self.module_install_dir / f"build__{self.module_name}.log"
        )

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Build and install Boost")
    parser.add_argument("--build-type", choices=[build_type.value for build_type in environment.BuildType], required=True)
    parser.add_argument("--link-type", choices=[link_type.value for link_type in environment.LinkType], required=True)
    args = parser.parse_args()

    env = environment.current(
        build_type=environment.BuildType(args.build_type),
        link_type=environment.LinkType(args.link_type)
    )
    builder_boost(env).build()

if(__name__ == "__main__"):
    main()
