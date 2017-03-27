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
    sfz = SFZParser(args['<sfzfile>'])
    multisamp = Multisample()
    multisamp.initFromSFZ(sfz)
    multisamp.write()

    return


class Multisample(object):
    name = 'default'
    samples = []
    sfzSampleBasePath = None

    def __init__(self, sfz=None):
        pass

    def initFromSFZ(self, sfz):
        defaultPath = None

        self.name = "{}".format(os.path.splitext(sfz.path)[0])

        for section in sfz.sections:
            sectionName = section[0]
            logging.debug("=== section <{}>".format(sectionName))
            if sectionName == "control":
                for k, v in section[1].items():
                    logging.debug(" {}={}".format(k,v))
                    if k == "default_path":
                        defaultPath = os.path.join(os.path.dirname(os.path.abspath(sfz.path)),os.path.normpath(v.replace('\\','/')))
                        self.sfzSampleBasePath = defaultPath
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
                newsample['sample-stop'] = self.getsamplecount(newsampleFullPath)
                newsample['tune'] = '0.0'
                newsample['track'] = 'true'
                newsample['loopmode'] = 'off'
                newsample['loopstart'] = '0.000'
                newsample['loopstop'] = '0.000'

                self.samples.append(newsample)

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
        zf = zipfile.ZipFile(outpath,mode='w',compression=zipfile.ZIP_DEFLATED)
        try:
            zf.writestr('multisample.xml',xml)
            samplesWritten = []
            for sample in self.samples:
                samplepath = os.path.join(self.sfzSampleBasePath,sample['file'])
                if samplepath not in samplesWritten:
                    zf.write(samplepath,sample['file'])
                    samplesWritten.append(samplepath)
        finally:
            zf.close


    def getsamplecount(self, path):
        ifile = wave.open(path)
        sampcount = ifile.getnframes()

        return sampcount


class SFZParser(object):
    # sfz parsing based off https://github.com/SpotlightKid/sfzparser/blob/master/sfzparser.py
    rx_section = re.compile('^<([^>]+)>\s?')

    def __init__(self, path, encoding=None, **kwargs):
        self.encoding = encoding
        self.path = path
        self.groups = [] #TODO.. not sure function of groups in sfz or if they translate to multisample
        self.sections = []

        with open(path, encoding=self.encoding or 'utf-8') as sfz:
            self.parse(sfz)

    def parse(self, sfz):
        sections = self.sections
        cur_section = {}
        value = None

        for line in sfz:
            line = line.strip()
            #strip out comments
            line = re.sub('//.+$','',line)

            if not line:
                continue

            while line:
                match = self.rx_section.search(line)
                if match:
                    if cur_section:
                        sections.append((section_name, cur_section))
                        cur_section = {}

                    section_name = match.group(1).strip()
                    line = line[match.end():].lstrip()
                elif "=" in line:
                    line, _, value = line.rpartition('=')
                    if '=' in line:
                        line, key = line.rsplit(None, 1)
                        cur_section[key] = value
                        value = None
                elif value:
                    line, key = None, line
                    cur_section[key] = value
                else:
                    logging.warning("ignoring line: {}", line)
                    break

        if cur_section:
            sections.append((section_name, cur_section))

        return sections


if __name__ == "__main__":
    main()
