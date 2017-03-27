Full spec at: [http://drealm.info/sfz/plj-sfz.xhtml#what]

## Example .sfz file

    <control>
    default_path=Strings\Harp\

    <global>
    ampeg_attack=0.001
    ampeg_release=12
    ampeg_dynamic=1
    volume=0

    <group> //Begin Group for entire instrument

    <region>
    sample=KSHarp_G1_mp.wav
    lokey=30
    hikey=32
    pitch_keycenter=31
    lovel=0
    hivel=127
    volume=10

    <region>
    sample=KSHarp_A2_mf.wav
    lokey=43
    hikey=46
    pitch_keycenter=45
    lovel=0
    hivel=127
    volume=10

    <region>
    sample=KSHarp_A4_mf.wav
    lokey=67
    hikey=70
    pitch_keycenter=69
    lovel=0
    hivel=127
    volume=10


## Section headers

### \<control>
    default_path = Strings\Harp\

### \<global>

### \<group>

### \<region>
    sample = KSHarp_G1_mp.wav
    lokey = (note code)
    hikey = (note code)
    pitch_keycenter = (note code)
    lovel = (0-127) velocity range covered by this sample
    hivel = (0-127)
    volume = 10 (unknown, dbs? 10 max?)

### \<curve>
### \<effect>


### note codes
    c-1 = 0
    ...
    c2  = 36
    c#2 = 37
    d2  = 38
    d#2 = 39
    e2  = 40
    f2  = 41
    f#2 = 42
    g2  = 43
    g#2 = 44
    a3  = 45
    a#3 = 46
    b3  = 47
    c3  = 48
    ...
    c9  = 120
    ...
    g9  = 127

