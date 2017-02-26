#!/usr/bin/env python

import argparse
import os
import re
import shutil
import sys

def shifttime(vect, step, offset, time):
    time += step
    if time < 0:
        return ['00', '00', '00', '000']
    # millis
    if time%1000 < 100:
        if time%1000 < 10:
            vect[3] = '00' + str(time%1000)
        else:
            vect[3] = '0' + str(time%1000)
    else:
        vect[3] = str(time%1000)
    time /= 1000
    # seconds
    if time%60 == 0:
        vect[2] = '00'
    elif time%60 < 10:
        vect[2] = '0' + str(time%60)
    else:
        vect[2] = str(time%60)
    time -= time%60
    # minutes
    if time%3600 == 0:
        vect[1] = '00'
    elif time%3600/60 < 10:
        vect[1] = '0' + str(time%3600/60)
    else:
        vect[1] = str(time%3600/60)
    time -= time%3600
    # hours
    if time/3600 == 0:
        vect[0] = '00'
    elif time/3600 < 10:
        vect[0] = '0' + str(time/3600)
    else:
        vect[0] = str(time/3600)
    return vect

def shift(filename, value, offset):
    try:
        f = open(filename, "r")
    except IOError:
        print 'File "%s" not found' % filename
        sys.exit(1)

    lines = f.readlines()
    f.close()

    fullpath = os.getcwd() + '/' + os.path.basename(filename)

    # make a copy
    shutil.copyfile(fullpath, fullpath + '.old')
    os.remove(fullpath)

    filexists = 1
    try:
        f = open(fullpath, "r")
    except IOError:
        # file does not exist, we can create one
        filexists = 0
        try:
            f.close()
            f = open(fullpath, "w")
        except Exception, e:
            print e
            sys.exit(1)
    if filexists:
        f.close()
        res = raw_input('File "' + fullpath +
                        '" already exists, wanna overwrite it? '
                        '(y/n)\n> ')
        if res.lower() != 'y':
            sys.exit(0)
        else:
            os.remove(fullpath)
            try:
                f = open(fullpath, "w")
            except Exception, e:
                print e
                sys.exit(1)

    for s in lines:
        match = re.search("^[\s]*[0-9]{1,2}:"
                          "[0-9]{1,2}:"
                          "[0-9]{1,2},[0-9]{1,3}"
                          "[\s]+-->[\s]+"
                          "[0-9]{1,2}:"
                          "[0-9]{1,2}:"
                          "[0-9]{1,2},[0-9]{1,3}[\s]*", s)
        if match is not None:
            pattern = re.compile("[0-9]{1,2}:"
                                 "[0-9]{1,2}:"
                                 "[0-9]{1,2},[0-9]{1,3}")
            chunks = re.findall(pattern, match.group())

            # first timestamp
            begin = chunks[0].split(':')
            begin = [begin[0],
                     begin[1],
                     begin[2].split(',')[0],
                     begin[2].split(',')[1]]
            # second timestamp
            end = chunks[1].split(':')
            end = [end[0], end[1],
                   end[2].split(',')[0],
                   end[2].split(',')[1]]

            # convert in millis
            time = int(begin[3]) + int(begin[2])*1000 +\
                int(begin[1])*60*1000 + int(begin[0])*60*60*1000

            if offset is not None and time < offset:
                # no need to shift
                f.write(begin[0] + ':' + begin[1] + ':' +
                        begin[2] + ',' + begin[3])
                f.write(' --> ')
                f.write(end[0] + ':' + end[1] + ':' + end[2] + ',' + end[3])
                f.write('\r\n')
                continue

            # shift first timestamp
            begin = shifttime(begin, value, offset, time)
            if begin is None:
                print "ERROR: begin is none " , chunks
                continue

            f.write(begin[0] + ':' + begin[1] + ':' + begin[2] +
                    ',' + begin[3])

            f.write(' --> ')

            # convert in millis
            time = int(end[3]) + int(end[2])*1000 +\
                int(end[1])*60*1000 + int(end[0])*60*60*1000
            # shift second timestamp
            end = shifttime(end, value, offset, time)
            if end is None:
                print "ERROR: end is none " , chunks
                continue

            f.write(end[0] + ':' + end[1] + ':' + end[2] + ',' + end[3])
            f.write('\r\n')
        else:
            f.write(s)
    f.close()

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Shift subtitles file'
                                                 'backward/forward of a '
                                                 'millisecond value.',
                                     epilog='Example of use: python subshifter'
                                            ' -f 14500 -o 1:10:37'
                                            ' subtitles-file.srt')
    parser.add_argument('file', help='path to subtitles file')
    parser.add_argument('-f', '--forward', metavar='NUM', type=int,
                        help='number of millisec to shift forward')
    parser.add_argument('-b', '--backward', metavar='NUM', type=int,
                        help='number of millisec to shift backward')
    parser.add_argument('-o', '--offset',
                        help='offset [[Hours:]Minutes:]Seconds - subtitles will'
                        ' be shifted starting from this timestamp')
    args = parser.parse_args()

    if args.forward is None and args.backward is None:
        print "Either forward or backward shift value must be specified."
        parser.print_help()
        sys.exit(1)
    if args.forward is not None and args.backward is not None:
        print "Only one option between forward and backward can be specified."
        parser.print_help()
        sys.exit(1)
    if args.forward is None:
        step = int(args.backward*-1)
    else:
        step = int(args.forward)
    offset = 0
    if args.offset is not None:
        match = re.search("^("
                          "([0-9]+:[0-5]{0,1}[0-9]{1}:)" # hours & minutes
                          "|"
                          "([0-5]{0,1}[0-9]{1}:)" # minutes only
                          "){0,1}"
                          "[0-9]{1,2}$", args.offset)
        if match is not None:
            chunks = args.offset.split(':')
            for i in range(0, len(chunks)):
                if i is 0:
                    offset += int(chunks[::-1][i])*1000
                else:
                    offset += 60**i*int(chunks[::-1][i])*1000
            print "Valid offset format:", offset, "ms"
        else:
            print "Invalid offset format"
            sys.exit(1)
    shift(args.file, step, offset)

