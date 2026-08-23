#!/usr/bin/env python3

import platform

from .environment_base import BuildType as BuildType
from .environment_base import LinkType  as LinkType
from .environment_base import environment_base as base
from .environment_win  import environment_win  as win
from .environment_linux import environment_linux as linux


def current(*, build_type:BuildType, link_type:LinkType):
    system = platform.system()
    if system == "Windows":
        return win(build_type=build_type, link_type=link_type)
    if system == "Linux":
        return linux(build_type=build_type, link_type=link_type)
    raise RuntimeError(f"Unsupported platform: {system}")

