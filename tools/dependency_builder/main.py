#!/usr/bin/env python3

import argparse

import builder

import environment

def main():
    parser = argparse.ArgumentParser(description="Build and install all dependencies")
    parser.add_argument("--build-type", choices=[build_type.value for build_type in environment.BuildType], required=True)
    parser.add_argument("--link-type", choices=[link_type.value for link_type in environment.LinkType], required=True)
    args = parser.parse_args()

    env = environment.current(
        build_type=environment.BuildType(args.build_type),
        link_type=environment.LinkType(args.link_type)
    )

    builder.openssl(env).build()
    builder.boost(env).build()
    builder.json(env).build()
    builder.spdlog(env).build()

    builder.zlib(env).build()
    builder.zstd(env).build()

    builder.ngtcp2(env).build()
    builder.nghttp2(env).build()
    builder.nghttp3(env).build()

if(__name__ == "__main__"):
    main()
