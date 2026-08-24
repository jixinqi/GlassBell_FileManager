#!/usr/bin/env python3

import sys
import pathlib
import hashlib
import json
import shutil
import urllib.request
import zipfile

dependency_builder_dir = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(dependency_builder_dir))

import environment as environment

if __package__ in (None, ""):
    from builder_base import builder_base
else:
    from .builder_base import builder_base

class builder_openssl(builder_base):
    def __init__(self, env):
        super().__init__("openssl", env)

    def __find_perl(self):
        tools_dir = self.env.output_dir / "tools"
        strawberry_dir = tools_dir / "strawberry-perl"
        perl_exe = strawberry_dir / "perl" / "bin" / "perl.exe"
        if(perl_exe.exists()):
            return perl_exe.as_posix()

        perl_spec_file = pathlib.Path(__file__).parent / "build_spec" / "openssl" / "perl.json"
        with open(perl_spec_file, "r", encoding="utf-8") as input_file:
            perl_spec = json.load(input_file)["windows"]

        tools_dir.mkdir(parents=True, exist_ok=True)
        archive_file = tools_dir / perl_spec["download_url"].rsplit("/", 1)[-1]
        print(f'Perl was not found; downloading {perl_spec["download_url"]}')
        urllib.request.urlretrieve(perl_spec["download_url"], archive_file)

        digest = hashlib.sha256()
        with open(archive_file, "rb") as input_file:
            for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
                digest.update(chunk)

        if(digest.hexdigest() != perl_spec["sha256"]):
            archive_file.unlink()
            raise RuntimeError("The downloaded Strawberry Perl archive failed SHA-256 verification")

        if(strawberry_dir.exists()):
            shutil.rmtree(strawberry_dir)
        with zipfile.ZipFile(archive_file) as archive:
            archive.extractall(strawberry_dir)

        return perl_exe.as_posix()

    def build_impl(self):
        build_type_option = f'--{self.env.build_type.value.lower()}'
        link_type_option = "shared" if self.env.link_type.value == "Shared" else "no-shared"
        openssl_config_dir = self.module_install_dir / "ssl"

        if(isinstance(self.env, environment.win)):
            # no-asm avoids the AVX-IFMA perlasm incompatibility with MSVC on Windows;
            # no-makedepend avoids nmake's U1055 on the huge DEPS list.
            perl_exe = self.__find_perl()
            configure_command = (
                f'"{perl_exe}" Configure VC-WIN64A'
                f' --prefix="{self.module_install_dir.as_posix()}"'
                f' --openssldir="{openssl_config_dir.as_posix()}"'
                f' {build_type_option}'
                f' {link_type_option}'
                f' no-tests no-docs no-makedepend no-asm'
            )
            commands = [
                configure_command,
                "nmake",
                "nmake install_sw",

                # Configure/nmake generate some files (apps/CA.pl, include/openssl/*.h, ...)
                # with the Windows read-only attribute. Clear it so the next build's
                # shutil.rmtree() on the pre_build dir does not fail with Access Denied.
                f'attrib -R /s /d "{self.module_pre_build_dir.as_posix()}/*"'
            ]
        elif(isinstance(self.env, environment.linux)):
            configure_command = (
                f'perl ./Configure linux-x86_64'
                f' --prefix="{self.module_install_dir.as_posix()}"'
                f' --openssldir="{openssl_config_dir.as_posix()}"'
                f' {build_type_option}'
                f' {link_type_option}'
                f' no-tests no-docs no-makedepend'
            )
            commands = [
                configure_command,
                "make -j4",
                "make install_sw"
            ]
        else:
            raise RuntimeError(f"Unsupported environment: {type(self.env).__name__}")

        self.env.run_commands(
            commands = commands,
            cwd = self.module_pre_build_dir,
            log_file = self.module_install_dir / f"build__{self.module_name}.log"
        )

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Build and install OpenSSL")
    parser.add_argument("--build-type", choices=[build_type.value for build_type in environment.BuildType], required=True)
    parser.add_argument("--link-type", choices=[link_type.value for link_type in environment.LinkType], required=True)
    args = parser.parse_args()

    env = environment.current(
        build_type=environment.BuildType(args.build_type),
        link_type=environment.LinkType(args.link_type)
    )
    builder_openssl(env).build()

if(__name__ == "__main__"):
    main()
