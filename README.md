# sf2bitwig

Converts sfz instruments into Bitwig Studio multisample instruments.

The Bitwig multisample format is more basic than sfz. Features that are unique to sfz will be lost in the conversion process.

## Usage
python sf2bitwig.py file.sfz

## Dependencies
* docopt

## Tested SFZ files

### No issues

[VS Chamber Orchestra: Community Edition](https://github.com/sgossner/VSCO-2-CE)
[SFZ FLukelele Sampled Ukelele: Community Edition](http://patcharena.com/sfz-flukelele-sampled-ukelele-sfz-format/)
[PatchArena Free Casio CK-10 Sample Pack](http://patcharena.com/free-casio-ck-10-sample-pack/)
[Warm Strings SFZ](http://patcharena.com/downloads/comment.php?dlid=1247)
[Double Bass Pizz](http://patcharena.com/downloads/comment.php?dlid=1256)

### Have issues

[Sonatina Symphonic Orchestra](http://sso.mattiaswestlund.net/download.html)
* Some .sfz cause issues on case sensitive file systems (easy to fix by hand)
* Some .sfz have regions with missing pitch_keycenter opcode (causes region to play out of tune, can be fixed by hand)

[PatchArena Marimba: Community Edition](http://patcharena.com/free-marimba-samples-patcharena-marimba-in-sfz-format/)
* Resulting multisample does not load

## SFZ resources
http://patcharena.com/downloads/index.php?subcat=168
[unofficial sfz spec](http://drealm.info/sfz/plj-sfz.xhtml)
