#!/usr/bin/env python3

VERSION="0.2.0" # MAJOR.MINOR.PATCH | http://semver.org

from sfzparser import SFZParser
from sfzparser import sfz_note_to_midi_key
from collections import defaultdict
from io import open

import zipfile
import wave
import re
import os
import operator


def main(args=None):
    # Parse command line
    for fn in args:
        # Convert file
        multisamp = Multisample()
        multisamp.initFromSFZ(fn)
        multisamp.write()

    return


class Multisample(object):
    name = 'default'
    samples = []

    def __init__(self, sfz=None):
        pass

    def initFromSFZ(self, sfzfile):
        cur_global_defaults = {}
        cur_control_defaults = {}
        cur_group_defaults = {}
        sfz_opcodes_ignored = defaultdict(int)

        print("\nConverting {} to multisample".format(sfzfile))
        sfz = SFZParser(sfzfile)
        #print("Finished parsing {}".format(sfzfile))

        self.name = "{}".format(os.path.splitext(sfzfile)[0])

        for section in sfz.sections:
            sectionName = section[0]
            #print("start section <{}>".format(sectionName))
            if sectionName == "control":
                cur_control_defaults = {}
                for k, v in section[1].items():
                    cur_control_defaults[k] = v
                    if k == "default_path":
                        cur_control_defaults["default_path"] = os.path.join(os.path.dirname(os.path.abspath(sfzfile)),os.path.normpath(v.replace('\\','/')))

                    #print("Set control default: {}={}".format(k,cur_control_defaults[k]))

            elif sectionName == "group":
                cur_group_defaults = {}
                for k, v in section[1].items():
                    cur_group_defaults[k] = v
                    #print("Set group default: {}={}".format(k,v))

            elif sectionName == "global":
                cur_global_defaults = {}
                for k, v in section[1].items():
                    cur_global_defaults[k] = v
                    #print("Set global default: {}={}".format(k,v))

            elif sectionName == "region":
                newsample = {}

                # Apply settings with priority global < group < region
                opcodes = dict(cur_global_defaults)
                opcodes.update(cur_group_defaults)
                opcodes.update(section[1])

                for k, v in opcodes.items():
                    #print(" {}={}".format(k,v))
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
                        sfz_opcodes_ignored["{}={}".format(k,v)] += 1

                defaultPath = cur_control_defaults.get('default_path',os.path.dirname(os.path.abspath(sfzfile)))
                newsampleFullPath = os.path.join(defaultPath,newsample['file'])
                newsample['filepath'] = newsampleFullPath
                newsample['sample-start'] = '0.000'
                newsample['sample-stop'] = self.getsamplecount(newsampleFullPath)

                if 'root' not in newsample and newsample['track'] == 'true':
                    print("ERROR: No pitch_keycenter for sample {}, root of sample will need to be manually adjusted in Bitwig".format(newsample['file']))
                    newsample['root'] = 0 # bitwig defaults to c4 when root is not given, make the issue more obvious with a more extreme value

                if newsample['filepath'] not in [s['filepath'] for s in self.samples]:
                    self.samples.append(newsample)
                    #print("Converted sample {}".format(newsample['file']))
                else:
                    print("WARNING: Skipping duplicate sample: {} ({})".format(os.path.basename(newsample.get('file','')),newsample.get('filepath','')))

            elif sectionName == "global":
                for k, v in section[1].items():
                    sfz_opcodes_ignored["{}={}".format(k,v)] += 1
                    #print("WARNING: Ignoring SFZ opcode {}={}".format(k,v))
            elif sectionName == "group":
                for k, v in section[1].items():
                    sfz_opcodes_ignored["{}={}".format(k,v)] += 1
                    #print("WARNING: Ignoring SFZ opcode {}={}".format(k,v))
            elif sectionName == "curve":
                    sfz_opcodes_ignored["{}={}".format(k,v)] += 1
                    #print("WARNING: Ignoring SFZ opcode {}={}".format(k,v))
            elif sectionName == "effect":
                    sfz_opcodes_ignored["{}={}".format(k,v)] += 1
                    #print("WARNING: Ignoring SFZ opcode {}={}".format(k,v))
            elif sectionName == "comment":
                pass
            else:
                print("WARNING: Unhandled section {}".format(sectionName))
                sfz_opcodes_ignored["{}={}".format(k,v)] += 1

        print("Finished converting {} to multisample, {} samples extracted".format(sfzfile,len(self.samples)))

        if sfz_opcodes_ignored:
            print("\nSFZ opcodes that were lost in translation:")
            sorted_sfz_opcodes_ignored = sorted(sfz_opcodes_ignored.items(), key=operator.itemgetter(1), reverse=True)

            for v in sorted_sfz_opcodes_ignored:
                print("({})  {}".format(v[1],v[0]))

        sfz_ahdsr_opcodes = ['ampeg_release', 'ampeg_sustain', 'ampeg_hold', 'ampeg_decay', 'ampeg_attack']
        suggest_ahdsr = { k: v for k, v in sfz_opcodes_ignored.items() if k.split('=')[0] in sfz_ahdsr_opcodes }
        if suggest_ahdsr:
            print("\nSuggested Bitwig sampler AHDSR settings:")
            ahdsr = self.getbestahdsr(suggest_ahdsr)

            print("({})  A = {} s".format(ahdsr['attack'][1],ahdsr['attack'][0]))
            print("({})  H = {} %".format(ahdsr['hold'][1],ahdsr['hold'][0]))
            print("({})  D = {} s".format(ahdsr['decay'][1],ahdsr['decay'][0]))
            print("({})  S = {} %".format(ahdsr['sustain'][1],ahdsr['sustain'][0]))
            print("({})  R = {} s".format(ahdsr['release'][1],ahdsr['release'][0]))



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

        print("\nWriting multisample {}".format(outpath))

        # Build zip containing multisample.xml and sample files
        zf = zipfile.ZipFile(outpath,mode='w',compression=zipfile.ZIP_DEFLATED)
        try:
            #print("Adding multisample.xml")
            zf.writestr('multisample.xml',xml)
            for sample in self.samples:
                #print("Adding sample: {} ({})".format(os.path.basename(sample.get('file','')),sample.get('filepath','')))
                zf.write(sample.get('filepath',''),os.path.basename(sample.get('file','')))

        finally:
            zf.close
            print("Finished writing multisample {}".format(outpath))

    def getbestahdsr(self, histogram):
        ahdsr = { 'attack':[None,0], 'hold':[None,0], 'decay':[None,0], 'sustain':[None,0], 'release':[None,0]  }

        for k, v in histogram.items():
            settingName, settingValue = k.split('=')
            settingName = settingName.split('_')[1]
            confidence = v

            if confidence > ahdsr[settingName][1]:
                ahdsr[settingName][0] = settingValue
                ahdsr[settingName][1] = confidence

        return ahdsr


    def getsamplecount(self, path):
        ifile = wave.open(path)
        sampcount = ifile.getnframes()

        return sampcount


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:] or None))
