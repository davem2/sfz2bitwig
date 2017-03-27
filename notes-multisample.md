## Example multisample xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<multisample name="Freak Ass Vibraphone">
   <generator>Bitwig Studio</generator>
   <category>Mallets</category>
   <creator>Genys</creator>
   <description/>
   <keywords>
      <keyword>acoustic</keyword>
      <keyword>clean</keyword>
   </keywords>
   <layer name="Default">
      <sample file="Freak Ass Vibraphone F2 01.wav" gain="0.000" sample-start="0.000" sample-stop="623932.000" tune="0.0">
         <key high="53" low="36" root="53" track="true"/>
         <velocity high="49"/>
         <loop mode="off" start="0.000" stop="623932.000"/>
      </sample>
      <sample file="Acoustic Piano (Nektar) FF A#3.wav" gain="0.000" sample-start="0.000" sample-stop="139650.000" tune="0.0">
         <key high="72" low="68" root="70" track="true"/>
         <velocity/>
         <loop mode="sustain" start="107296.000" stop="139481.000"/>
      </sample>
   </layer>
</multisample>
```

## Fields
### \<sample>

#### attribs
    file = "Freak Ass Vibraphone F2 01.wav" (sample filename)
    gain = "0.000" (db?)
    sample-start = "0.000" (samples?)
    sample-stop = "623932.000" (samples?)

#### elements

##### \<key>
    high = (note code)
    low = (note code)
    root = (note code)
    track = (true,false)
    tune = "0.0" (-1, to 1)(measured in semitones, 5cents == 0.05)

##### \<velocity>
    high = (0-127) not needed when high=127
    low = (0-127) not needed when low=0

    * If high or low values are given when they are not needed, then the Bitwig audio engine deactivates when multisample instrument is loaded
##### \<loop>
    mode = (off,sustain,others?)
    start = "0.000" (samples?)
    stop = "623932.000" (samples?)

## Note codes
    c-2 = 0
    ...
    c1  = 36
    c#1 = 37
    d1  = 38
    d#1 = 39
    e1  = 40
    f1  = 41
    f#1 = 42
    g1  = 43
    g#1 = 44
    a2  = 45
    a#2 = 46
    b2  = 47
    c2  = 48
    ...
    c8  = 120
    ...
    g8  = 127



