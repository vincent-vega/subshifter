# subshifter
Subtitle shifter tool

usage: subshifter.py [-h] [-f DELTA] [-b DELTA] [-o OFFSET] file

Shift subtitle timestampsforward/backward.

positional arguments:
  file                  path to subtitles file

options:
  -h, --help            show this help message and exit
  -f DELTA, --forward DELTA
                        shift DELTA ms forward
  -b DELTA, --backward DELTA
                        shift DELTA ms backward
  -o OFFSET, --offset OFFSET
                        offset [[Hours:]Minutes:]Seconds - subtitles will be
                        shifted starting from this instant

Example of use: python subshifter -f 14500 -o 1:10:37 subtitles-file.srt
