#!/usr/bin/env python3

import shutil
import abc
import os
import sys
import pathlib
dependency_builder_dir = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(dependency_builder_dir))

import environment as environment

class builder_base(abc.ABC):
    def __init__(self, module_name:str, env:environment.base):
        self.env                  = env
        self.module_name          = module_name
        self.module_source_dir    = env.project_dir  / "third_party" / self.module_name
        self.module_pre_build_dir = env.pre_build_dir                / self.module_name
        self.module_build_dir     = env.build_dir                    / self.module_name
        self.module_install_dir   = env.install_dir                  / self.module_name

    def build(self):
        if(self.module_pre_build_dir.exists()): shutil.rmtree(self.module_pre_build_dir)
        if(self.module_build_dir.exists()):     shutil.rmtree(self.module_build_dir)
        if(self.module_install_dir.exists()):   shutil.rmtree(self.module_install_dir)

        self.module_build_dir.mkdir(parents=True)
        shutil.copytree(
            self.module_source_dir,
            self.module_pre_build_dir,
            ignore=shutil.ignore_patterns(".git")
        )
        self.build_impl()

    @abc.abstractmethod
    def build_impl(self):
        pass

if(__name__ == "__main__"):
    os._exit(1)
