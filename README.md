# sfz2bitwig

Converts sfz instruments into Bitwig Studio multisample instruments.

The Bitwig multisample format is more basic than sfz. Features that are unique to sfz will be lost in the conversion process.

## Usage
Simple usage, convert file.sfz into file.multisample:
```shell
python sfz2bitwig.py file.sfz
```

Multiple files can be converted at once:
```shell
python sfz2bitwig.py file.sfz file2.sfz ...
```

Metadata of the created multisample can be set through commandline arguments:
```shell
python sfz2bitwig.py --category Strings --creator bob --keywords acoustic warm orchestral --description 'multisample description' file.sfz file2.sfz ...
```

By default, sfz2bitwig will scan for and extract embedded loop points from wav samples. To disable this (faster conversions) use the --noloop option.
```shell
python sfz2bitwig.py --noloop file.sfz
```


## Thanks
* [SpotlightKid](https://github.com/SpotlightKid) for [sfzparser code](https://github.com/SpotlightKid/sfzparser)
* [Joseph Basquin](https://github.com/josephernest), for [wav loop point extraction code](https://gist.github.com/josephernest/3f22c5ed5dabf1815f16efa8fa53d476)

## Tested SFZ files

### No issues
[VS Chamber Orchestra: Community Edition](https://github.com/sgossner/VSCO-2-CE)

[SFZ FLukelele Sampled Ukelele: Community Edition](http://patcharena.com/sfz-flukelele-sampled-ukelele-sfz-format/)

[PatchArena Free Casio CK-10 Sample Pack](http://patcharena.com/free-casio-ck-10-sample-pack/)

[Warm Strings SFZ](http://patcharena.com/downloads/comment.php?dlid=1247)

[Double Bass Pizz](http://patcharena.com/downloads/comment.php?dlid=1256)

[City Piano](http://bigcatinstruments.blogspot.com/2015/09/all-keyboard-instruments.html)

[Iowa Piano](http://bigcatinstruments.blogspot.com/2015/09/all-keyboard-instruments.html)

[Open Source Drum Kit Project](http://download.linuxaudio.org/musical-instrument-libraries/sfz/the_open_source_drumkit.tar.7z)


### Have issues
[Sonatina Symphonic Orchestra](http://sso.mattiaswestlund.net/download.html)
* Some .sfz cause issues on case sensitive file systems (easy to fix by hand)
* Some .sfz have regions with missing pitch_keycenter opcode (causes region to play out of tune, can be fixed by hand)
* A version with the above corrections made can be found [here](https://github.com/davem2/sso), also check out [this version with loop points added](https://github.com/peastman/sso)

[PatchArena Marimba: Community Edition](http://patcharena.com/free-marimba-samples-patcharena-marimba-in-sfz-format/)
* Resulting multisample does not load (something strange about PatchArena_marimba-036-c#1.wav)

## SFZ resources
http://patcharena.com/downloads/index.php?subcat=168

[unofficial sfz spec](http://drealm.info/sfz/plj-sfz.xhtml)
