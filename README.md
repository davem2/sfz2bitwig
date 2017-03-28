# sf2bitwig

Converts sfz instruments into Bitwig Studio multisample instruments.

The Bitwig multisample format is more basic than sfz. Features that are unique to sfz will be lost in the conversion process.

## Usage
python sf2bitwig.py file.sfz

## Dependencies
* docopt

## Tested SFZ files

[VS Chamber Orchestra: Community Edition](https://github.com/sgossner/VSCO-2-CE)
* No issues found

[Sonatina Symphonic Orchestra](http://sso.mattiaswestlund.net/download.html)
* Some .sfz cause issues on case sensitive file systems (easy to fix by hand)
* Some .sfz have regions with missing pitch_keycenter opcode (causes region to play out of tune, can be fixed by hand)
