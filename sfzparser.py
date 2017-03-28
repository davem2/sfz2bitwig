#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A parser for SFZ files.
original at https://github.com/SpotlightKid/sfzparser/blob/master/sfzparser.py
"""

import math
import re

from collections import OrderedDict
from io import open


SFZ_NOTE_LETTER_OFFSET = {'a': 9, 'b': 11, 'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7}


def sfz_note_to_midi_key(sfz_note):
    letter = sfz_note[0].lower()
    if letter not in SFZ_NOTE_LETTER_OFFSET.keys():
        return sfz_note

    sharp = '#' in sfz_note
    octave = int(sfz_note[-1])
    #return SFZ_NOTE_LETTER_OFFSET[letter] + ((octave + 1) * 12) + (1 if sharp else 0)
    #Notes in bitwig multisample are an octave different (i.e. c4=60, not c3=60)
    return SFZ_NOTE_LETTER_OFFSET[letter] + ((octave + 2) * 12) + (1 if sharp else 0)


def freq_to_cutoff(param):
    return 127. * max(0, min(1, math.log(param / 130.) / 5)) if param else None


class SFZParser(object):
    rx_section = re.compile('^<([^>]+)>\s?')

    def __init__(self, sfz_path, encoding=None, **kwargs):
        self.encoding = encoding
        self.sfz_path = sfz_path
        self.groups = []
        self.sections = []

        with open(sfz_path, encoding=self.encoding or 'utf-8') as sfz:
            self.parse(sfz)

    def parse(self, sfz):
        sections = self.sections
        cur_section = []
        value = None

        for line in sfz:
            line = line.strip()

            if not line:
                continue

            if line.startswith('//'):
                sections.append(('comment', line))
                continue

            while line:
                match = self.rx_section.search(line)
                if match:
                    if cur_section:
                        sections.append((section_name, OrderedDict(reversed(cur_section))))
                        cur_section = []

                    section_name = match.group(1).strip()
                    line = line[match.end():].lstrip()
                elif "=" in line:
                    line, _, value = line.rpartition('=')
                    if '=' in line:
                        line, key = line.rsplit(None, 1)
                        cur_section.append((key, value))
                        value = None
                elif value:
                    line, key = None, line
                    cur_section.append((key, value))
                else:
                    if line.startswith('//'):
                        print("Warning: inline comment")
                        sections.append(('comment', line))
                    # ignore garbage
                    break

        if cur_section:
            sections.append((section_name, OrderedDict(reversed(cur_section))))

        return sections


if __name__ == '__main__':
    import pprint
    import sys
    parser = SFZParser(sys.argv[1])
    pprint.pprint(parser.sections)
