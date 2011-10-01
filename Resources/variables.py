import os, sys, unicodedata, codecs
from types import UnicodeType

reload(sys)
sys.setdefaultencoding("utf-8")

constants = dict()
constants["VERSION"] = "0.1.0"
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
                   "Prefs": 1006, "MidiLearn": 1007, "Run": 1008, "ResetKeyboard": 1009, "ExportChord": 1010, 
                   "Modules": 1100, "About": 5999, "Tutorial": 6000, "MidiLearnHelp": 6001, "ExportHelp": 6002, "CloseTut": 7000,
                   "CloseHelp": 7001, "CloseLFO": 7002, "DeSelect": 9998, "Select": 9999, "Uniform": 10000, "Triangular": 10001, 
                   "Minimum": 10002, "Jitter": 10003}
constants["VARIABLE_NAMES"] = ["AUDIO_HOST", "OUTPUT_DRIVER", "MIDI_INTERFACE", "SR", "PYO_PRECISION", "FORMAT", "BITS", 
                               "POLY", "AUTO_OPEN", "SLIDERPORT", "CUSTOM_MODULES_PATH", "EXPORT_PATH"]
constants["VAR_PREF_LABELS"] = {"FORMAT": 'Exported soundfile format', "SR": 'Sampling rate', 
                                "AUTO_OPEN": 'Auto open default or last synth', "POLY": 'Keyboard polyphony',
                                "PYO_PRECISION": 'Internal sample precision', "BITS": 'Exported sample type', 
                                "CUSTOM_MODULES_PATH": 'User-defined modules file', 
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
    if type(unistr) != UnicodeType:
        for encoding in encodings:
            try:
                unistr = unistr.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
            except:
                unistr = "UnableToDecodeString"
                print "Unicode encoding not in a recognized format..."
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
            if not lines[0].startswith("### Zyne") or not constants["VERSION"] in lines[0]:
                print "Zyne preferences out-of-date, using default values."
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
            elif key == "AUDIO_HOST" and not constants["OSX_BUILD_WITH_JACK_SUPPORT"] and prefs[key] == "Jack":
                vars[key] = ensureNFD("Portaudio")
            else:
                vars[key] = prefs[key]

checkForPreferencesFile()
