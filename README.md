# subshifter
Subtitle shifter tool

```
usage: subshifter.py [-h] [-f DELTA] [-b DELTA] [-o OFFSET] file.srt

Shift subtitle timestamps forward/backward.

positional arguments:
  file.srt              path to the subtitles file

options:
  -h, --help            show this help message and exit
  -f DELTA, --forward DELTA
                        shift DELTA ms forward
  -b DELTA, --backward DELTA
                        shift DELTA ms backward
  -o OFFSET, --offset OFFSET
                        offset [[Hours:]Minutes:]Seconds - subtitles will be
                        shifted starting from this instant

Example of use: python3 subshifter.py -f 14500 -o 1:10:37 /path/to/subtitles.srt
```
