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

import zipfile
import wave
import re
from io import open
import os
import logging


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

    def __init__(self, sfz=None):
        pass

    def initFromSFZ(self, sfzfile):
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

            if sectionName == "group":
                cur_group_defaults = {}
                for k, v in section[1].items():
                    cur_group_defaults[k] = v
                    logging.debug("Set group default: {}={}".format(k,v))

            elif sectionName == "region":
                newsample = {}

                opcodes = dict(cur_group_defaults)
                opcodes.update(dict(section[1]))

                for k, v in opcodes.items():
                    logging.debug(" {}={}".format(k,v))
                    if k == "sample":
                        newsample['file'] = v
                    elif k == "lokey":
                        newsample['keylow'] = v
                    elif k == "hikey":
                        newsample['keyhigh'] = v
                    elif k == "pitch_keycenter":
                        newsample['root'] = v
                    elif k == "key":
                        newsample['keylow'] = v
                        newsample['keyhigh'] = v
                        newsample['root'] = v
                    elif k == "lovel":
                        newsample['velocitylow'] = v
                    elif k == "hivel":
                        newsample['velocityhigh'] = v
                    elif k == "volume":
                        newsample['gain'] = v
                    else:
                        logging.warning("Ignoring opcode {}={}".format(k,v))

                # TODO: finish loops/pitch etc..
                newsample['sample-start'] = '0.000'
                newsampleFullPath = os.path.join(cur_control_defaults["default_path"],newsample['file'])
                newsample['filepath'] = newsampleFullPath
                newsample['sample-stop'] = self.getsamplecount(newsampleFullPath)
                newsample['tune'] = '0.0'
                newsample['track'] = 'true'
                newsample['loopmode'] = 'off'
                newsample['loopstart'] = '0.000'
                newsample['loopstop'] = '0.000'

                self.samples.append(newsample)
                logging.debug("Converted sample {}".format(newsample['file']))

            elif sectionName == "global":
                for k, v in section[1].items():
                    logging.warning("Ignoring opcode {}={}".format(k,v))
            elif sectionName == "group":
                for k, v in section[1].items():
                    logging.warning("Ignoring opcode {}={}".format(k,v))
            elif sectionName == "curve":
                for k, v in section[1].items():
                    logging.warning("Ignoring opcode {}={}".format(k,v))
            elif sectionName == "effect":
                for k, v in section[1].items():
                    logging.warning("Ignoring opcode {}={}".format(k,v))

            else:
                logging.warning("Unhandled section {}".format(sectionName))

            #TODO handle loops? tuning? sample start/end?


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
            xml += '      <sample file="{}" gain="{}" sample-start="{}" sample-stop="{}">\n'.format(sample.get('file',''),sample.get('gain',''),sample.get('sample-start',''),sample.get('sample-stop',''))
            xml += '         <key high="{}" low="{}" root="{}" track="{}" tune="{}"/>\n'.format(sample.get('keyhigh',''),sample.get('keylow',''),sample.get('root',''),sample.get('track',''),sample.get('tune',''))
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

            xml += '         <loop mode="{}" start="{}" stop="{}"/>\n'.format(sample.get('loopmode',''),sample.get('loopstart',''),sample.get('loopstop',''))
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
                    logging.debug("Adding sample: {} ({})".format(sample.get('file',''),sample.get('filepath','')))
                    zf.write(sample.get('filepath',''),sample.get('file',''))
                    samplesWritten.append(sample.get('filepath',''))
                else:
                    logging.warning("Skipping duplicate sample: {} ({})".format(sample.get('file',''),sample.get('filepath','')))

        finally:
            zf.close
            logging.info("Generated multisample {}".format(outpath))


    def getsamplecount(self, path):
        ifile = wave.open(path)
        sampcount = ifile.getnframes()

        return sampcount


if __name__ == "__main__":
    main()
