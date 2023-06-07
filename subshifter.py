#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import argparse
import os
import re
import shutil
import sys


def _shifttime(delta: int, instant: int) -> str:
    instant += delta
    if instant < 0:
        return '00:00:00:000'
    # millis
    milliseconds = str(instant % 1000).zfill(3)
    instant = int(instant / 1000)
    # seconds
    seconds = str(instant % 60).zfill(2)
    instant -= instant % 60
    # minutes
    minutes = str(int(instant % 3600 / 60)).zfill(2)
    instant -= instant % 3600
    # hours
    hours = str(int(instant / 3600)).zfill(2)
    return f'{hours}:{minutes}:{seconds},{milliseconds}'


def _millis(values: [int, int, int, int]) -> int:
    return sum(map(lambda x: x[0] * x[1], zip([3600000, 60000, 1000, 1], values)))


def shift(file: str, delta: int, offset: int) -> None:
    backup = f'{file}.backup'
    if Path(backup).exists():
        resp = None
        while resp is None or resp not in 'yYnN':
            resp = input(f'File {backup} will be overwritten, continue? (y/N) ')
        if resp in 'nN':
            print('Aborted')
            sys.exit(0)
        os.remove(backup)
    shutil.copy2(file, backup)
    os.remove(file)
    timestamp_pattern = r'\d{1,2}:\d{1,2}:\d{1,2},\d{1,3}'
    with open(backup) as fr, open(file, 'w') as fw:
        while (line := fr.readline()):
            match = re.search(f'^\\s*({timestamp_pattern})\\s+-->\\s+({timestamp_pattern})\\s*$', line)
            if not match:
                fw.write(line)
                continue
            timestamp1, timestamp2 = match.groups()

            # first timestamp
            start = map(int, re.findall(r'\d+', timestamp1))
            millis = _millis(start)
            if offset is not None and millis < offset:
                # no need to shift
                fw.write(line)
                continue
            fw.write(f'{_shifttime(delta, millis)} --> ')

            # second timestamp
            end = map(int, re.findall(r'\d+', timestamp2))
            fw.write(f'{_shifttime(delta, _millis(end))}\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Shift subtitle timestamps'
                                                 ' forward/backward.',
                                     epilog=f'Example of use: python3 {os.path.basename(__file__)}'
                                            ' -f 14500 -o 1:10:37'
                                            ' /path/to/subtitles.srt')
    parser.add_argument('file.srt', help='path to the subtitles file')
    parser.add_argument('-f', '--forward', metavar='DELTA', type=int,
                        help='shift DELTA ms forward')
    parser.add_argument('-b', '--backward', metavar='DELTA', type=int,
                        help='shift DELTA ms backward')
    parser.add_argument('-o', '--offset',
                        help='offset [[Hours:]Minutes:]Seconds - subtitles will'
                        ' be shifted starting from this instant')
    args = parser.parse_args()

    if args.forward is None and args.backward is None:
        print("Either forward or backward values are required")
        parser.print_help()
        sys.exit(1)
    if args.forward is not None and args.backward is not None:
        print("Only one option between forward and backward is allowed")
        parser.print_help()
        sys.exit(1)
    delta = int(args.backward * -1) if args.forward is None else int(args.forward)
    offset = 0
    if args.offset is not None and re.match('^('
                                            r'(\d+:[0-5]?\d:)'  # hours & minutes
                                            '|'
                                            r'([0-5]?\d:)'  # minutes only
                                            ')?'
                                            r'[0-5]?\d$', args.offset):
        time_chunks = list(map(int, re.findall(r'\d+', args.offset)))
        for idx, n in enumerate(time_chunks[::-1]):
            offset += 60 ** idx * n * 1000
        print(f"Starting at offset: {offset}ms")
    elif args.offset is not None:
        print("Invalid offset format")
        sys.exit(1)
    shift(args.file, delta, offset)
