#!/usr/bin/python3
#
# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) 2022-2025 MangDang


def main():
    try:
        from MangDang.mini_pupper.display import Display
    except ImportError:
        print(
            'ERROR: MangDang BSP not found. '
            'Install the Noble-compatible Mini Pupper BSP before running show_ip. '
            'See: https://github.com/MangDang/mini_pupper_bsp'
        )
        raise SystemExit(1)
    display = Display()
    display.show_ip()


if __name__ == '__main__':
    main()
