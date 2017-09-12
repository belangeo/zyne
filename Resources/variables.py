import os, sys, unicodedata, codecs

if sys.version_info[0] < 3:
    unicode_t = unicode
else:
    unicode_t = str

constants = dict()
constants["VERSION"] = "0.1.2"
constants["YEAR"] = "2012"
constants["PLATFORM"] = sys.platform
constants["OSX_BUILD_WITH_JACK_SUPPORT"] = False
constants["DEFAULT_ENCODING"] = sys.getdefaultencoding()
constants["SYSTEM_ENCODING"] = sys.getfilesystemencoding()

if '/Zyne.app' in os.getcwd():
    constants["RESOURCES_PATH"] = os.getcwd()
    currentw = os.getcwd()
    spindex = currentw.index('/Zyne.app')
    os.chdir(currentw[:spindex])
else:
    constants["RESOURCES_PATH"] = os.path.join(os.getcwd(), 'Resources')

if not os.path.isdir(constants["RESOURCES_PATH"]) and constants["PLATFORM"] == "win32":
    constants["RESOURCES_PATH"] = os.path.join(os.getenv("ProgramFiles"), "Zyne", "Resources")

constants["DEFAULT_PREFS"] = """
AUDIO_HOST = Portaudio
OUTPUT_DRIVER = ""
MIDI_INTERFACE = ""
SR = 48000
PYO_PRECISION = double
FORMAT = wav
BITS = 24
POLY = 5
SLIDERPORT = 0.05
AUTO_OPEN = Default
CUSTOM_MODULES_PATH = ""
EXPORT_PATH = ""
LAST_SAVED = ""

"""

constants["ID"] = {"New": 1000, "Open": 1001, "Save": 1002, "SaveAs": 1003, "Export": 1004, "Quit": 1005,
                   "Prefs": 1006, "MidiLearn": 1007, "Run": 1008, "ResetKeyboard": 1009, "ExportChord": 1010, "Retrig": 1011,
                   "ExportTracks": 1012, "ExportChordTracks": 1013, "UpdateModules": 2000, "CheckoutModules": 2001,
                   "Modules": 1100, "About": 5999, "Tutorial": 6000, "MidiLearnHelp": 6001, "ExportHelp": 6002, "CloseTut": 7000,
                   "CloseHelp": 7001, "CloseLFO": 7002, "DeSelect": 9998, "Select": 9999, "Uniform": 10000, "Triangular": 10001, 
                   "Minimum": 10002, "Jitter": 10003, "Duplicate": 10100}
constants["VARIABLE_NAMES"] = ["AUDIO_HOST", "OUTPUT_DRIVER", "MIDI_INTERFACE", "SR", "PYO_PRECISION", "FORMAT", "BITS", 
                               "POLY", "AUTO_OPEN", "SLIDERPORT", "CUSTOM_MODULES_PATH", "EXPORT_PATH"]
constants["VAR_PREF_LABELS"] = {"FORMAT": 'Exported soundfile format', "SR": 'Sampling rate', 
                                "AUTO_OPEN": 'Auto open default or last synth', "POLY": 'Keyboard polyphony',
                                "PYO_PRECISION": 'Internal sample precision', "BITS": 'Exported sample type', 
                                "CUSTOM_MODULES_PATH": 'User-defined modules location', 
                                "SLIDERPORT": "Slider's portamento in seconds", 
                                "AUDIO_HOST": "Audio host API",
                                "OUTPUT_DRIVER":'Prefered output driver', 
                                "MIDI_INTERFACE": 'Prefered Midi interface', 
                                "EXPORT_PATH": 'Prefered path for exported samples'}
constants["VAR_CHOICES"] =  {"FORMAT": ['wav', 'aif'], "SR": ['44100', '48000', '96000'], 
                             "AUTO_OPEN": ['None', 'Default', 'Last Saved'], "BITS": ['16', '24', '32'],
                            "POLY": [str(i) for i in range(1,21)], "PYO_PRECISION": ['single', 'double']}


vars = dict()
vars["AUDIO_HOST"] = "Portaudio"
vars["OUTPUT_DRIVER"] = ""
vars["MIDI_INTERFACE"] = ""
vars["SR"] = 48000
vars["FORMAT"] = 'wav'
vars["BITS"] = 24
vars["POLY"] = 5
vars["SLIDERPORT"] = 0.05
vars["PYO_PRECISION"] = "double"
vars["CUSTOM_MODULES_PATH"] = ""
vars["EXPORT_PATH"] = ""
vars["AUTO_OPEN"] = 'Default'
vars["LAST_SAVED"] = ""
vars["MIDILEARN"] = False
vars["LEARNINGSLIDER"] = None

vars["EXTERNAL_MODULES"] = {}
vars["MIDIPITCH"] = None
vars["MIDIVELOCITY"] = 0.707
vars["NOTEONDUR"] = 1.0
vars["VIRTUAL"] = False
vars["MIDI_ACTIVE"] = 0

def ensureNFD(unistr):
    if constants["PLATFORM"] in ['linux2', 'win32']:
        encodings = [constants["DEFAULT_ENCODING"], constants["SYSTEM_ENCODING"],
                     'cp1252', 'iso-8859-1', 'utf-16']
        format = 'NFC'
    else:
        encodings = [constants["DEFAULT_ENCODING"], constants["SYSTEM_ENCODING"],
                     'macroman', 'iso-8859-1', 'utf-16']
        format = 'NFD'
    if type(unistr) != unicode_t:
        for encoding in encodings:
            try:
                unistr = unistr.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
            except:
                unistr = "UnableToDecodeString"
                print("Unicode encoding not in a recognized format...")
                break
    return unicodedata.normalize(format, unistr)

def toSysEncoding(unistr):
    try:
        if constants["PLATFORM"] == "win32":
            unistr = unistr.encode(constants["SYSTEM_ENCODING"])
        else:
            unistr = unicode(unistr)
    except:
        pass
    return unistr

vars["ensureNFD"] = ensureNFD
vars["toSysEncoding"] = toSysEncoding

def checkForPreferencesFile():
    preffile = os.path.join(os.path.expanduser("~"), ".zynerc")
    if os.path.isfile(preffile):
        with codecs.open(preffile, "r", encoding="utf-8") as f:
            lines = f.readlines()
            pref_rel_version = int(lines[0].split()[3].split(".")[1])
            cur_rel_version = int(constants["VERSION"].split(".")[1])
            if lines[0].startswith("### Zyne"):
                if pref_rel_version != cur_rel_version: 
                    print("Zyne preferences out-of-date, using default values.")
                    lines = constants["DEFAULT_PREFS"].splitlines()
            else:
                print("Zyne preferences out-of-date, using default values.")
                lines = constants["DEFAULT_PREFS"].splitlines()
        prefs = dict()
        for line in lines[1:]:
            line = line.strip()
            if line:
                sline = line.split("=")
                prefs[sline[0].strip()] = ensureNFD(sline[1].strip())
        for key in prefs.keys():
            if key in ["SR", "POLY", "BITS"]:
                vars[key] = int(prefs[key])
            elif key in ["SLIDERPORT"]:
                vars[key] = float(prefs[key])
            elif key == "AUDIO_HOST" and constants["PLATFORM"] == "darwin" and not constants["OSX_BUILD_WITH_JACK_SUPPORT"] and prefs[key] in ["Jack", "Coreaudio"]:
                vars[key] = ensureNFD("Portaudio")
            else:
                vars[key] = prefs[key]

checkForPreferencesFile()
