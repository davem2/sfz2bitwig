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
        logging.info("Converting {} to multisample".format(sfzfile))
        defaultPath = None
        sfz = SFZParser(sfzfile)
        logging.debug("Finished parsing {}".format(sfzfile))

        self.name = "{}".format(os.path.splitext(sfzfile)[0])

        for section in sfz.sections:
            sectionName = section[0]
            logging.debug("start section <{}>".format(sectionName))
            if sectionName == "control":
                for k, v in section[1].items():
                    logging.debug(" {}={}".format(k,v))
                    if k == "default_path":
                        defaultPath = os.path.join(os.path.dirname(os.path.abspath(sfzfile)),os.path.normpath(v.replace('\\','/')))
                        logging.debug("defaultPath changed to {}".format(defaultPath))
                    else:
                        logging.error("Unhandled key {}".format(k))

            elif sectionName == "region":
                newsample = {}
                newsample['file'] = None
                newsample['keylow'] = 0
                newsample['keyhigh'] = 127
                newsample['root'] = 0
                newsample['velocitylow'] = 0
                newsample['velocityhigh'] = 127

                for k, v in section[1].items():
                    logging.debug(" {}={}".format(k,v))
                    if k == "sample":
                        newsample['file'] = v
                    elif k == "lokey":
                        newsample['keylow'] = v
                    elif k == "hikey":
                        newsample['keyhigh'] = v
                    elif k == "pitch_keycenter":
                        newsample['root'] = v
                    elif k == "lovel":
                        newsample['velocitylow'] = v
                    elif k == "hivel":
                        newsample['velocityhigh'] = v
                    elif k == "volume":
                        #TODO how does volume translate to gain?
                        #newsample['gain'] = v
                        newsample['gain'] = 0
                    else:
                        logging.error("Unhandled key {}".format(k))

                newsample['gain'] = '0.000'
                newsample['sample-start'] = '0.000'
                newsampleFullPath = os.path.join(defaultPath,newsample['file'])
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
                    logging.debug(" {}={}".format(k,v))
            elif sectionName == "group":
                for k, v in section[1].items():
                    logging.debug(" {}={}".format(k,v))
            elif sectionName == "curve":
                for k, v in section[1].items():
                    logging.debug(" {}={}".format(k,v))
            elif sectionName == "effect":
                for k, v in section[1].items():
                    logging.debug(" {}={}".format(k,v))

            else:
                logging.error("Unhandled section {}".format(sectionName))

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
            xml += '      <sample file="{}" gain="{}" sample-start="{}" sample-stop="{}">\n'.format(sample['file'],sample['gain'],sample['sample-start'],sample['sample-stop'])
            xml += '         <key high="{}" low="{}" root="{}" track="{}" tune="{}"/>\n'.format(sample['keyhigh'],sample['keylow'],sample['root'],sample['track'],sample['tune'])
            vhigh = int(sample['velocityhigh'])
            vlow = int(sample['velocitylow'])
            if vhigh == 127 and vlow == 0:
                xml += '         <velocity/>\n'
            elif vlow == 0:
                xml += '         <velocity high="{}"/>\n'.format(vhigh)
            elif vhigh == 127:
                xml += '         <velocity low="{}"/>\n'.format(vlow)
            else:
                xml += '         <velocity high="{}" low="{}"/>\n'.format(vhigh,vlow)

            xml += '         <loop mode="{}" start="{}" stop="{}"/>\n'.format(sample['loopmode'],sample['loopstart'],sample['loopstop'])
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
                if sample['filepath'] not in samplesWritten:
                    logging.debug("Adding sample: {} ({})".format(sample['file'],sample['filepath']))
                    zf.write(sample['filepath'],sample['file'])
                    samplesWritten.append(sample['filepath'])
                else:
                    logging.warning("Skipping duplicate sample: {} ({})".format(sample['file'],sample['filepath']))

        finally:
            zf.close
            logging.info("Generated multisample {}".format(outpath))


    def getsamplecount(self, path):
        ifile = wave.open(path)
        sampcount = ifile.getnframes()

        return sampcount


if __name__ == "__main__":
    main()
