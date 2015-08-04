
```
#!/usr/bin/env python
# encoding: utf-8
"""
Created by belangeo on 2010-11-25.
"""
from pyo import *
import os, sys

if len(sys.argv) < 2:
    print "SimpleSampler must be called with a sound folder path in argument!"
    sys.exit()
else:
    path = sys.argv[1]

pm_list_devices()

s = Server(sr=44100, nchnls=2, buffersize=256, duplex=0)
dev = input("Enter your midi device number : ")
s.setMidiInputDevice(dev)
s.boot()

snds = sorted([f for f in os.listdir(path) if f[-4:].lower() in [".wav", ".aif"]])

print "loading soundfiles..."

objs = []
for i, f in enumerate(snds):
    t = SndTable(os.path.join(path,f))
    n = Notein(1,0,i+36,i+36)
    pl = TrigEnv(Thresh(n["velocity"]), t, t.getDur(), mul=Port(n["velocity"],.001,1)).out()
    objs.extend([t,n,pl])

print "Done."

s.gui(locals())

```

## Usage ##

```
>>> python SimpleSampler.py path_to_sound_folder
pyo version 0.5.1 (uses single precision)
MIDI input devices:
0 : Midi KeyStation
1 : IAC bus 1
Enter your midi device number : 0
loading soundfiles...
Done.
```