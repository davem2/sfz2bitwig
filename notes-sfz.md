Full(ish) spec at: [http://drealm.info/sfz/plj-sfz.xhtml]

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

Opcodes in <global> and <group> are applied to all <region> sections within that group/file. If duplicate opcodes are found priority is given to <region> over <group> over <global>

### \<control>
    default_path = Strings\Harp\

### \<global>
    Opcodes here will be applied to all regions

### \<group>
    Opcodes here will be applied to all regions in this group

### \<region>


### \<curve>
### \<effect>


## Opcodes
    sample = KSHarp_G1_mp.wav
    lokey = (note code or letter)
    hikey = (note code or letter)
    pitch_keycenter = (note code or letter)
    key = (note code or letter) shortcut to set lokey,hikey and pitch_keycenter to the same note
    pitch_keytrack = (bool? have only seen pitch_keytrack=0, defaults to true when opcode is not present)
    lovel = (0-127) velocity range covered by this sample
    hivel = (0-127)
    volume = 10 (dbs)
    tune = (-100 to 100) cents
    transpose = (-127 to 127) semitones
    loop_mode = one_shot - play whole sample once
                loop_continuous - loop until the amplitude EG reaches zero; default if loop points defined
                loop_sustain - loop until Release and then play through to the end point or amplitude EG reaching zero
    loop_start = (0 to 4Gb) offset in samples
    loop_end = (0 to 4Gb) offset in samples
    offset = (0 to 4Gb) offset in samples
    end = (0 to 4Gb) offset in samples

    pan = (?)
    seq_length
    seq_position

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

