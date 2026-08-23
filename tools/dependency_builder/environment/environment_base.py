#!/usr/bin/env python3

import os
import pathlib
import threading
import abc
import enum

class BuildType(enum.Enum):
    DEBUG = "Debug"
    RELEASE = "Release"

class LinkType(enum.Enum):
    SHARED = "Shared"
    STATIC = "Static"

class environment_base(abc.ABC):
    def __init__(self, *, build_type:BuildType, link_type:LinkType, output_dir_name:str="build"):
        self.__env           = None
        self.__mutex         = threading.Lock()

        self.__build_type    = build_type
        self.__link_type     = link_type

        self.__project_dir   = pathlib.Path(__file__).parent.parent.parent.parent
        self.__output_dir    = self.__project_dir / output_dir_name
        configuration_dir    = self.__output_dir / self.__build_type.value / self.__link_type.value
        self.__pre_build_dir = configuration_dir / "pre_build"
        self.__build_dir     = configuration_dir / "build"
        self.__install_dir   = configuration_dir / "install"

    @property
    def build_type(self):
        return self.__build_type

    @property
    def link_type(self):
        return self.__link_type

    @property
    def mutex(self):
        return self.__mutex

    @property
    def project_dir(self):
        return self.__project_dir

    @property
    def output_dir(self):
        return self.__output_dir

    @property
    def pre_build_dir(self):
        return self.__pre_build_dir

    @property
    def build_dir(self):
        return self.__build_dir

    @property
    def install_dir(self):
        return self.__install_dir

    @abc.abstractmethod
    def run_commands(self, commands:list[str], cwd:pathlib.Path, log_file:pathlib.Path):
        pass

if(__name__ == "__main__"):
    os._exit(1)
