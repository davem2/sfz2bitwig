#!/usr/bin/env python3

"""sfz2bitwig

Usage:
  sfz2bitwig [options] <sfzfile>
  sfz2bitwig -h | --help
  sfz2bitwig ---version

Convert an sfz instrument into a Bitwig multisample instrument.

Examples:
  sfz2bitwig instrument.sfz

Options:
  -q, --quiet           Print less text.
  -v, --verbose         Print more text.
  -h, --help            Show help.
  --version             Show version.
"""

VERSION="0.1.0" # MAJOR.MINOR.PATCH | http://semver.org

from docopt import docopt

from sfzparser import SFZParser
from sfzparser import sfz_note_to_midi_key
from collections import defaultdict
from io import open

import zipfile
import wave
import re
import os
import logging
import operator


def main():
    # Parse command line
    args = docopt(__doc__, version="sfz2bitwig v{}".format(VERSION))

    # Configure logging
    logLevel = logging.INFO #default
    if args['--verbose']:
        logLevel = logging.DEBUG
    elif args['--quiet']:
        logLevel = logging.ERROR

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logLevel)
    logging.debug(args)

    # Convert file
    multisamp = Multisample()
    multisamp.initFromSFZ(args['<sfzfile>'])
    multisamp.write()

    return


class Multisample(object):
    name = 'default'
    samples = []
    sfz_opcodes_ignored = defaultdict(int)

    def __init__(self, sfz=None):
        pass

    def initFromSFZ(self, sfzfile):
        cur_global_defaults = {}
        cur_control_defaults = {}
        cur_group_defaults = {}

        logging.info("Converting {} to multisample".format(sfzfile))
        sfz = SFZParser(sfzfile)
        logging.debug("Finished parsing {}".format(sfzfile))

        self.name = "{}".format(os.path.splitext(sfzfile)[0])

        for section in sfz.sections:
            sectionName = section[0]
            logging.debug("start section <{}>".format(sectionName))
            if sectionName == "control":
                cur_control_defaults = {}
                for k, v in section[1].items():
                    cur_control_defaults[k] = v
                    if k == "default_path":
                        cur_control_defaults["default_path"] = os.path.join(os.path.dirname(os.path.abspath(sfzfile)),os.path.normpath(v.replace('\\','/')))

                    logging.debug("Set control default: {}={}".format(k,cur_control_defaults[k]))

            elif sectionName == "group":
                cur_group_defaults = {}
                for k, v in section[1].items():
                    cur_group_defaults[k] = v
                    logging.debug("Set group default: {}={}".format(k,v))

            elif sectionName == "global":
                cur_global_defaults = {}
                for k, v in section[1].items():
                    cur_global_defaults[k] = v
                    logging.debug("Set global default: {}={}".format(k,v))

            elif sectionName == "region":
                newsample = {}

                # Apply settings with priority global < group < region
                opcodes = dict(cur_global_defaults)
                opcodes.update(cur_group_defaults)
                opcodes.update(section[1])

                for k, v in opcodes.items():
                    logging.debug(" {}={}".format(k,v))
                    if k == "sample":
                        newsample['file'] = os.path.normpath(v.replace('\\','/'))
                        if newsample['file'][0] == '/': # relative path should not contain leading slash
                            newsample['file'] = newsample['file'][1:]
                    elif k == "lokey":
                        newsample['keylow'] = sfz_note_to_midi_key(v)
                    elif k == "hikey":
                        newsample['keyhigh'] = sfz_note_to_midi_key(v)
                    elif k == "pitch_keycenter":
                        newsample['root'] = sfz_note_to_midi_key(v)
                    elif k == "key":
                        newsample['keylow'] = sfz_note_to_midi_key(v)
                        newsample['keyhigh'] = sfz_note_to_midi_key(v)
                        newsample['root'] = sfz_note_to_midi_key(v)
                    elif k == "pitch_keytrack":
                        newsample['track'] = v
                    elif k == "lovel":
                        newsample['velocitylow'] = v
                    elif k == "hivel":
                        newsample['velocityhigh'] = v
                    elif k == "volume":
                        newsample['gain'] = v
                    elif k == "tune":
                        newsample['tune'] = int(v) * 0.01
                    elif k == "loop_mode":
                        if v != 'one_shot':
                            newsample['loopmode'] = 'sustain' # bitwig currently supports off or sustain
                    elif k == "loop_start":
                        newsample['loopstart'] = v
                    elif k == "loop_end":
                        newsample['loopstop'] = v

                    else:
                        self.sfz_opcodes_ignored["{}={}".format(k,v)] += 1

                # TODO: finish loops
                defaultPath = cur_control_defaults.get('default_path',os.path.dirname(os.path.abspath(sfzfile)))
                newsampleFullPath = os.path.join(defaultPath,newsample['file'])
                newsample['filepath'] = newsampleFullPath
                newsample['sample-start'] = '0.000'
                newsample['sample-stop'] = self.getsamplecount(newsampleFullPath)

                if 'root' not in newsample and newsample['track'] == 'true':
                    logging.error("No pitch_keycenter for sample {}, root of sample will need to be manually adjusted in Bitwig".format(newsample['file']))
                    newsample['root'] = 0 # bitwig defaults to c4 when root is not given, make the issue more obvious with a more extreme value

                self.samples.append(newsample)
                logging.debug("Converted sample {}".format(newsample['file']))

            elif sectionName == "global":
                for k, v in section[1].items():
                    self.sfz_opcodes_ignored["{}={}".format(k,v)] += 1
                    #logging.warning("Ignoring SFZ opcode {}={}".format(k,v))
            elif sectionName == "group":
                for k, v in section[1].items():
                    self.sfz_opcodes_ignored["{}={}".format(k,v)] += 1
                    #logging.warning("Ignoring SFZ opcode {}={}".format(k,v))
            elif sectionName == "curve":
                    self.sfz_opcodes_ignored["{}={}".format(k,v)] += 1
                    #logging.warning("Ignoring SFZ opcode {}={}".format(k,v))
            elif sectionName == "effect":
                    self.sfz_opcodes_ignored["{}={}".format(k,v)] += 1
                    #logging.warning("Ignoring SFZ opcode {}={}".format(k,v))
            elif sectionName == "comment":
                pass
            else:
                logging.warning("Unhandled section {}".format(sectionName))
                self.sfz_opcodes_ignored["{}={}".format(k,v)] += 1


    def makexml(self):
        xml = ''

        xml += '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<multisample name="{}">\n'.format(self.name)
        xml += '   <generator>Bitwig Studio</generator>\n'
        xml += '   <category/>\n'
        xml += '   <creator>sfz2bitwig</creator>\n'
        xml += '   <description/>\n'
        xml += '   <keywords/>\n'
        xml += '   <layer name="Default">\n'

        for sample in self.samples:
            xml += '      <sample file="{}" gain="{}" sample-start="{}" sample-stop="{}">\n'.format(os.path.basename(sample.get('file','')),sample.get('gain','0.00'),sample.get('sample-start','0.000'),sample.get('sample-stop','0.000'))
            xml += '         <key high="{}" low="{}" root="{}" track="{}" tune="{}"/>\n'.format(sample.get('keyhigh',''),sample.get('keylow',''),sample.get('root',''),sample.get('track','true'),sample.get('tune','0.0'))
            vhigh = int(sample.get('velocityhigh','127'))
            vlow = int(sample.get('velocitylow','0'))
            if vhigh == 127 and vlow == 0:
                xml += '         <velocity/>\n'
            elif vlow == 0:
                xml += '         <velocity high="{}"/>\n'.format(vhigh)
            elif vhigh == 127:
                xml += '         <velocity low="{}"/>\n'.format(vlow)
            else:
                xml += '         <velocity high="{}" low="{}"/>\n'.format(vhigh,vlow)

            xml += '         <loop mode="{}" start="{}" stop="{}"/>\n'.format(sample.get('loopmode','off'),sample.get('loopstart','0.000'),sample.get('loopstop',sample.get('sample-stop','0.000')))
            xml += '      </sample>\n'

        xml += '    </layer>\n'
        xml += '</multisample>\n'

        return xml


    def write(self, outpath=None):
        xml = self.makexml()

        if not outpath:
            outpath = "{}.multisample".format(self.name)

        # Build zip containing multisample.xml and sample files
        logging.debug("Building multisample zip container {}".format(outpath))
        zf = zipfile.ZipFile(outpath,mode='w',compression=zipfile.ZIP_DEFLATED)
        try:
            logging.debug("Adding multisample.xml")
            zf.writestr('multisample.xml',xml)
            samplesWritten = []
            for sample in self.samples:
                if sample.get('filepath','') not in samplesWritten:
                    logging.debug("Adding sample: {} ({})".format(os.path.basename(sample.get('file','')),sample.get('filepath','')))
                    zf.write(sample.get('filepath',''),os.path.basename(sample.get('file','')))
                    samplesWritten.append(sample.get('filepath',''))
                else:
                    logging.warning("Skipping duplicate sample: {} ({})".format(os.path.basename(sample.get('file','')),sample.get('filepath','')))

        finally:
            zf.close
            logging.info("Generated multisample {}".format(outpath))

        if self.sfz_opcodes_ignored:
            logging.info("SFZ opcodes that were lost in translation:")
            sorted_sfz_opcodes_ignored = sorted(self.sfz_opcodes_ignored.items(), key=operator.itemgetter(1), reverse=True)

            for v in sorted_sfz_opcodes_ignored:
                print("({})  {}".format(v[1],v[0]))

        suggest_ahdsr = { k: v for k, v in self.sfz_opcodes_ignored.items() if k.startswith('ampeg_') }
        if suggest_ahdsr:
            logging.info("Suggested Bitwig sampler AHDSR settings:")
            sorted_adsr_histogram = sorted(suggest_ahdsr.items(), key=operator.itemgetter(1), reverse=True)

            for v in sorted_adsr_histogram:
                print("({})  {}".format(v[1],v[0]))



    def getsamplecount(self, path):
        ifile = wave.open(path)
        sampcount = ifile.getnframes()

        return sampcount


if __name__ == "__main__":
    main()
