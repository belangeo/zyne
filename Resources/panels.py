# encoding: utf-8
import wx, os, math, copy, random
from wx.lib.stattext import GenStaticText
from wx.lib.statbmp import GenStaticBitmap
import Resources.variables as vars
from Resources.widgets import *
from pyolib._wxwidgets import VuMeter, BACKGROUND_COLOUR
from Resources.audio import *

MODULES =   {
            "FM": { "title": "--- Frequency Modulation ---", "synth": FmSynth, 
                    "p1": ["FM Ratio", .25, 0, 4, False, False],
                    "p2": ["FM Index", 5, 0, 40, False, False],
                    "p3": ["Lowpass Cutoff", 2000, 100, 18000, False, True]
                    },
            "Additive": { "title": "--- Additive Synthesis ---", "synth": AddSynth, 
                    "p1": ["Transposition", 0, -36, 36, True, False],
                    "p2": ["Spread", 1, 0, 2, False, False],
                    "p3": ["Feedback", 0, 0, 1, False, False]
                    },
            "Wind": { "title": "--- Wind Synthesis ---", "synth": WindSynth, 
                    "p1": ["Rand frequency", 1, 0.01, 20, False, True],
                    "p2": ["Rand Depth", .1, .001, .25, False, False],
                    "p3": ["Filter Q", 5, 1, 20, False, False]
                    },
            # "Phaser": { "title": "--- Phasing Synthesis ---", "synth": PhaserSynth, 
            #         "p1": ["Spread", 1.1, .25, 2, False, False],
            #         "p2": ["Bandwidth", .1, .001, 1, False, True],
            #         "p3": ["Feedback", .95, .9, 1, False, False]
            #         },
            "SquareMod": { "title": "--- Square Modulation ---", "synth": SquareMod, 
                    "p1": ["Harmonics", 10, 1, 40, True, False],
                    "p2": ["LFO Frequency", 1, .001, 20, False, False],
                    "p3": ["LFO Amplitude", 1, 0, 1, False, False]
                    },
            "SawMod": { "title": "--- Sawtooth Modulation ---", "synth": SawMod, 
                    "p1": ["Harmonics", 10, 1, 40, True, False],
                    "p2": ["LFO Frequency", 1, .001, 20, False, False],
                    "p3": ["LFO Amplitude", 1, 0, 1, False, False]
                    },
            "Pulsar": { "title": "--- Pulsar Synthesis ---", "synth": PulsarSynth, 
                    "p1": ["Harmonics", 10, 1, 20, True, False],
                    "p2": ["Transposition", 0, -36, 36, True, False],
                    "p3": ["LFO Frequency", 1, .02, 200, False, True],
                    },
            "Ross": { "title": "--- Rossler Attractors ---", "synth": Ross, 
                    "p1": ["Chaos", 0.5, 0., 1., False, False],
                    "p2": ["Chorus Depth", .001, .001, .125, False, True],
                    "p3": ["Lowpass Cutoff", 5000, 100, 15000, False, True]
                    },
            "Wave": { "title": "--- Waveform Synthesis ---", "synth": Wave, 
                    "p1": ["Waveform", 0, 0, 7, True, False],
                    "p2": ["Transposition", 0, -36, 36, True, False],
                    "p3": ["Sharpness", 0.5, 0., 1., False, False],
                    },
            "PluckedString": { "title": "--- Plucked String Synth ---", "synth": PluckedString, 
                    "p1": ["Transposition", 0, -48, 0, True, False],
                    "p2": ["Duration", 30, .25, 60, False, False],
                    "p3": ["Chorus Depth", .001, .001, .125, False, True]
                    },
            "Reson": { "title": "--- Resonators Synthesis ---", "synth": Reson, 
                    "p1": ["Transposition", 0, -36, 36, True, False],
                    "p2": ["Chorus Depth", .001, .001, .125, False, True],
                    "p3": ["Lowpass Cutoff", 2000, 100, 10000, False, True]
                    },
            }

LFO_CONFIG =    {
                "p1": ["Speed", 4, .01, 200, False, True],
                "p2": ["Waveform", 3, 0, 7, True, False],
                "p3": ["Jitter", 0, 0, 1, False, False]
                }

LFO_INIT = {"state": False, "params": [.001, .1, .7, 1, .1, 4, 3, 0], 
            "ctl_params": [None, None, None, None, None, None, None, None], "shown": False}
def get_lfo_init():
    return copy.deepcopy(LFO_INIT)

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
    
    def OnDropFiles(self, x, y, filename):
        self.window.GetTopLevelParent().openfile(filename[0])

class LFOFrame(wx.MiniFrame):
    def __init__(self, parent, synth, label, which):
        wx.MiniFrame.__init__(self, parent, -1, style=wx.FRAME_TOOL_WINDOW | wx.FRAME_FLOAT_ON_PARENT | wx.NO_BORDER)
        self.parent = parent
        self.SetMaxSize((230,250))
        self.SetSize((230,250))
        self.SetBackgroundColour(BACKGROUND_COLOUR)
        if vars.constants["PLATFORM"] == "darwin":
            close_accel = wx.ACCEL_CMD
        else:
            close_accel = wx.ACCEL_CTRL
        self.SetAcceleratorTable(wx.AcceleratorTable([
                                                        (wx.ACCEL_CTRL, ord("N"), vars.constants["ID"]["New"]), 
                                                        (wx.ACCEL_CTRL, ord("O"), vars.constants["ID"]["Open"]), 
                                                        (wx.ACCEL_CTRL, ord("S"), vars.constants["ID"]["Save"]), 
                                                        (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord("S"), vars.constants["ID"]["SaveAs"]), 
                                                        (wx.ACCEL_CTRL, ord("E"), vars.constants["ID"]["Export"]), 
                                                        (wx.ACCEL_CTRL, ord("M"), vars.constants["ID"]["MidiLearn"]),
                                                        (wx.ACCEL_CTRL, ord(","), vars.constants["ID"]["Prefs"]), 
                                                        (wx.ACCEL_CTRL, ord("G"), vars.constants["ID"]["Uniform"]), 
                                                        (wx.ACCEL_CTRL, ord("K"), vars.constants["ID"]["Triangular"]), 
                                                        (wx.ACCEL_CTRL, ord("L"), vars.constants["ID"]["Minimum"]), 
                                                        (wx.ACCEL_CTRL, ord("J"), vars.constants["ID"]["Jitter"]), 
                                                        (wx.ACCEL_CTRL, ord("Q"), vars.constants["ID"]["Quit"]), 
                                                        (close_accel, ord("W"), vars.constants["ID"]["CloseLFO"]), 
                                                     ]))
        self.Bind(wx.EVT_MENU, self.parent.onNew, id=vars.constants["ID"]["New"])
        self.Bind(wx.EVT_MENU, self.parent.onOpen, id=vars.constants["ID"]["Open"])
        self.Bind(wx.EVT_MENU, self.parent.onSave, id=vars.constants["ID"]["Save"])
        self.Bind(wx.EVT_MENU, self.parent.onSaveAs, id=vars.constants["ID"]["SaveAs"])
        self.Bind(wx.EVT_MENU, self.parent.onExport, id=vars.constants["ID"]["Export"])
        self.Bind(wx.EVT_MENU, self.onMidiLearnMode, id=vars.constants["ID"]["MidiLearn"])
        self.Bind(wx.EVT_MENU, self.parent.onPreferences, id=vars.constants["ID"]["Prefs"])
        self.Bind(wx.EVT_MENU, self.parent.onGenerateValues, id=vars.constants["ID"]["Uniform"], id2=vars.constants["ID"]["Jitter"])
        self.Bind(wx.EVT_MENU, self.parent.onQuit, id=vars.constants["ID"]["Quit"])
        self.Bind(wx.EVT_MENU, self.onClose, id=vars.constants["ID"]["CloseLFO"])
        self.mouseOffset = (0,0)
        self.which = which
        self.panel = LFOPanel(self, "LFO", "--- %s LFO ---" % label, synth, LFO_CONFIG["p1"], LFO_CONFIG["p2"], LFO_CONFIG["p3"], which)
        self.panel.SetPosition((0,0))
        self.panel.corner.Bind(wx.EVT_LEFT_DOWN, self.onMouseDown)
        self.panel.corner.Bind(wx.EVT_LEFT_UP, self.onMouseUp)
        self.panel.corner.Bind(wx.EVT_MOTION, self.onMotion)
        self.SetFocus()
    
    def onClose(self, evt):
        self.Hide()

    def onMidiLearnMode(self, evt):
        self.parent.onMidiLearnModeFromLfoFrame()

    def onMouseDown(self, evt):
        cornerPos = evt.GetPosition()
        offsetPos = self.panel.corner.GetPosition()
        self.mouseOffset = (offsetPos[0]+cornerPos[0], offsetPos[1]+cornerPos[1])
        self.panel.corner.CaptureMouse()

    def onMouseUp(self, evt):
        self.mouseOffset = (0,0)
        if self.panel.corner.HasCapture():
            self.panel.corner.ReleaseMouse()
        self.SetFocus()

    def onMotion(self, evt):
        if self.panel.corner.HasCapture():
            pos =  wx.GetMousePosition()
            self.SetPosition((pos[0]-self.mouseOffset[0], pos[1]-self.mouseOffset[1]))

    def get(self):
        params = [slider.GetValue() for slider in self.panel.sliders]
        ctl_params = [slider.midictl for slider in self.panel.sliders]
        return params, ctl_params
    
    def set(self, params, ctl_params):
        for i, p in enumerate(params):
            slider = self.panel.sliders[i]
            slider.SetValue(p)
            slider.outFunction(p)
        for i, p in enumerate(ctl_params):
            slider = self.panel.sliders[i]
            slider.setMidiCtl(p, False)
            if i in [5,6,7,8] and p != None:
                i4 = i - 5
                if self.panel.synth._params[self.which] != None:
                    self.panel.synth._params[self.which].assignLfoMidiCtl(p, slider, i4)

class LFOButtons(GenStaticText):
    def __init__(self, parent, label="LFO", synth=None, which=0, callback=None):
        GenStaticText.__init__(self, parent, -1, label=label, size=(30,12))
        self.parent = parent
        self.synth = synth
        self.which = which
        self.state = False
        self.callback = callback
        self.SetBackgroundColour(BACKGROUND_COLOUR)
        self.font, psize = self.GetFont(), self.GetFont().GetPointSize()
        if vars.constants["PLATFORM"] != "win32":
            self.font.SetWeight(wx.BOLD)
            
        if vars.constants["PLATFORM"] != "darwin":
            self.font.SetPointSize(psize-2)
        else:
            self.font.SetPointSize(psize-4)
        self.SetFont(self.font)
        self.Bind(wx.EVT_ENTER_WINDOW, self.hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.leave)
        self.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
        self.SetToolTip(wx.ToolTip("Click to enable, Shift+Click to open controls"))

    def setState(self, state):
        self.state = state
        self.parent.lfo_frames[self.which].panel.synth = self.synth
        if self.state:
            self.SetForegroundColour("#0000EE")
        else:
            self.SetForegroundColour("#000000")
        self.callback(self.which, self.state)
    
    def hover(self, evt):
        font, ptsize = self.GetFont(), self.GetFont().GetPointSize()
        font.SetPointSize(ptsize+1)
        self.SetFont(font)
        if self.state:
            self.SetForegroundColour("#0000CC")
        else:
            self.SetForegroundColour("#555555")
    
    def leave(self, evt):
        self.SetFont(self.font)
        if self.state:
            self.SetForegroundColour("#0000EE")
        else:
            self.SetForegroundColour("#000000")
    
    def MouseDown(self, evt):
        if evt.ShiftDown():
            self.parent.lfo_frames[self.which].panel.synth = self.synth
            pos = wx.GetMousePosition()
            self.parent.lfo_frames[self.which].SetPosition((pos[0]+5, pos[1]+5))
            self.parent.lfo_frames[self.which].Show()
            return
        if self.state:
            self.state = False
            self.SetForegroundColour("#000000")
        else:
            self.state = True
            self.SetForegroundColour("#0000EE")
        self.Refresh()
        self.callback(self.which, self.state)

class ServerPanel(wx.Panel):
    def __init__(self, parent, colour="#DDDDE7"):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.colour = colour
        self.SetBackgroundColour(colour)
        self.SetMinSize((230,500))
        self.fileformat = vars.vars["FORMAT"]
        self.sampletype = vars.vars["BITS"]
        self.virtualNotePressed = {}
        self.virtualvoice = 0
        self.keyboardShown = 0
        self.serverSettings = []
    
        self.fsserver = FSServer()
    
        dropTarget = MyFileDropTarget(self)
        self.SetDropTarget(dropTarget)
    
        self.title = wx.StaticText(self, id=-1, label="--- Server Controls ---", pos=(40,5))
   
        self.driverText = wx.StaticText(self, id=-1, label="Output Driver", pos=(15,25))
        if vars.vars["AUDIO_HOST"] != "Jack":
            preferedDriver = vars.vars["OUTPUT_DRIVER"]
            self.driverList, self.driverIndexes = get_output_devices()
            self.driverList = [vars.vars["ensureNFD"](driver) for driver in self.driverList]
            self.defaultDriver = get_default_output()
            self.popupDriver = wx.Choice(self, id=-1, pos=(13,40), size=(95, 20), choices=self.driverList)
            if preferedDriver and preferedDriver in self.driverList:
                driverIndex = self.driverIndexes[self.driverList.index(preferedDriver)]
                self.fsserver.shutdown()
                self.fsserver.setOutputDevice(driverIndex)
                self.fsserver.boot()
                self.popupDriver.SetStringSelection(preferedDriver)
            elif self.defaultDriver:
                self.popupDriver.SetSelection(self.driverIndexes.index(self.defaultDriver))
            self.popupDriver.Bind(wx.EVT_CHOICE, self.changeDriver)
        else:
            self.popupDriver = wx.Choice(self, id=-1, pos=(13,40), size=(95, 20), choices=[])
            self.popupDriver.Disable()

        preferedInterface = vars.vars["MIDI_INTERFACE"]
        self.interfaceText = wx.StaticText(self, id=-1, label="Midi interface", pos=(120,25))
        self.interfaceList, self.interfaceIndexes = get_midi_input_devices()
        self.interfaceList = [vars.vars["ensureNFD"](interface) for interface in self.interfaceList]
        if self.interfaceList != []:
            self.interfaceList.append("Virtual Keyboard")
            self.defaultInterface = get_midi_default_input()
            self.popupInterface = wx.Choice(self, id=-1, pos=(118,40), size=(95, 20), choices=self.interfaceList)
            if preferedInterface and preferedInterface in self.interfaceList:
                interfaceIndex = self.interfaceIndexes[self.interfaceList.index(preferedInterface)]
                self.fsserver.shutdown()
                self.fsserver.setMidiInputDevice(interfaceIndex)
                self.fsserver.boot()
                self.popupInterface.SetStringSelection(preferedInterface)
            elif self.defaultInterface:
                self.fsserver.shutdown()
                self.fsserver.setMidiInputDevice(self.defaultInterface)
                self.fsserver.boot()
                self.popupInterface.SetSelection(self.interfaceIndexes.index(self.defaultInterface))
        else:    
            self.popupInterface = wx.Choice(self, id=-1, pos=(118,40), size=(95, -1), choices=["No interface", "Virtual Keyboard"])
            self.popupInterface.SetSelection(1)
            wx.CallAfter(self.prepareForVirtualKeyboard)
        self.popupInterface.Bind(wx.EVT_CHOICE, self.changeInterface)
    
        self.srText = wx.StaticText(self, id=-1, label="Sample Rate", pos=(15,65))
        self.popupSr = wx.Choice(self, id=-1, pos=(13,80), size=(95,20), choices=["44100","48000","96000"])
        self.popupSr.SetStringSelection(str(vars.vars["SR"]))
        self.serverSettings.append(self.popupSr.GetSelection())
        self.popupSr.Bind(wx.EVT_CHOICE, self.changeSr)
        self.polyText = wx.StaticText(self, id=-1, label="Poly", pos=(120,65))
        self.popupPoly = wx.Choice(self, id=-1, pos=(118,80), size=(95,20), choices=[str(i) for i in range(1,21)])
        self.popupPoly.SetStringSelection(str(vars.vars["POLY"]))
        self.serverSettings.append(self.popupPoly.GetSelection())
        self.popupPoly.Bind(wx.EVT_CHOICE, self.changePoly)
    
        self.bitText = wx.StaticText(self, id=-1, label="Bits", pos=(15,105))
        self.popupBit = wx.Choice(self, id=-1, pos=(13,120), size=(95,20), choices=["16","24","32"])
        self.popupBit.SetStringSelection(str(vars.vars["BITS"]))
        self.serverSettings.append(self.popupBit.GetSelection())
        self.popupBit.Bind(wx.EVT_CHOICE, self.changeBit)
        self.formatText = wx.StaticText(self, id=-1, label="Format", pos=(120,105))
        self.popupFormat = wx.Choice(self, id=-1, pos=(118,120), size=(95,20), choices=["wav","aif"])
        self.popupFormat.SetStringSelection(vars.vars["FORMAT"])
        self.serverSettings.append(self.popupFormat.GetSelection())
        self.popupFormat.Bind(wx.EVT_CHOICE, self.changeFormat)
    
        self.onOffText = wx.StaticText(self, id=-1, label="Audio", pos=(15,145))
        self.onOff = wx.ToggleButton(self, id=-1, label="on / off", pos=(14,160), size=(95,20))
        self.onOff.Bind(wx.EVT_TOGGLEBUTTON, self.handleAudio)
        self.recText = wx.StaticText(self, id=-1, label="Record to disk", pos=(120,145))
        self.rec = wx.ToggleButton(self, id=-1, label="start / stop", pos=(119,160), size=(95,20))
        self.rec.Bind(wx.EVT_TOGGLEBUTTON, self.handleRec)
    
        self.textAmp = wx.StaticText(self, id=-1, label="Global Amplitude (dB)", pos=(15, 185), size=(200,20))
        self.sliderAmp = ZyneControlSlider(self, -60, 18, 0, pos=(15,200), outFunction=self.changeAmp, backColour=colour)
        self.serverSettings.append(1.0)
        self.meter = VuMeter(self)
        self.meter.SetPosition((15, 225))
        self.setAmpCallable()
    
        if vars.constants["PLATFORM"] == "darwin": 
            togWidth = 26
            togHeight = 16
        else: 
            togWidth = 30
            togHeight = 20
        self.ppEqTitle = wx.StaticText(self, id=-1, label="--- 4 bands equalizer", pos=(50,245))
        self.onOffEq = wx.ToggleButton(self, id=-1, label="On", pos=(15,245), size=(togWidth, togHeight))
        tog_font, tog_psize = self.onOffEq.GetFont(), self.onOffEq.GetFont().GetPointSize()
        if vars.constants["PLATFORM"] == "linux2":
            tog_font.SetPointSize(tog_psize-1)
        self.onOffEq.SetFont(tog_font)
        self.onOffEq.Bind(wx.EVT_TOGGLEBUTTON, self.handleOnOffEq)
        self.knobEqF1 = ControlKnob(self, 40, 250, 100, label='Freq 1', backColour=colour, outFunction=self.changeEqF1)
        self.knobEqF1.SetPosition((35, 265))
        self.knobEqF1.setFloatPrecision(2)
        self.knobEqF2 = ControlKnob(self, 300, 1000, 500, label='Freq 2', backColour=colour, outFunction=self.changeEqF2)
        self.knobEqF2.SetPosition((89, 265))
        self.knobEqF2.setFloatPrecision(2)
        self.knobEqF3 = ControlKnob(self, 1200, 5000, 2000, label='Freq 3', backColour=colour, outFunction=self.changeEqF3)
        self.knobEqF3.SetPosition((143, 265))
        self.knobEqF3.setFloatPrecision(2)
    
        self.knobEqA1 = ControlKnob(self, -40, 18, 0, label='B1 gain', backColour=colour, outFunction=self.changeEqA1)
        self.knobEqA1.SetPosition((12, 335))
        self.knobEqA2 = ControlKnob(self, -40, 18, 0, label='B2 gain', backColour=colour, outFunction=self.changeEqA2)
        self.knobEqA2.SetPosition((64, 335))
        self.knobEqA3 = ControlKnob(self, -40, 18, 0, label='B3 gain', backColour=colour, outFunction=self.changeEqA3)
        self.knobEqA3.SetPosition((116, 335))
        self.knobEqA4 = ControlKnob(self, -40, 18, 0, label='B4 gain', backColour=colour, outFunction=self.changeEqA4)
        self.knobEqA4.SetPosition((168, 335))
    
        self.ppCompTitle = wx.StaticText(self, id=-1, label="--- Dyn. compressor", pos=(50,408))
        self.onOffComp = wx.ToggleButton(self, id=-1, label="On", pos=(15,408), size=(togWidth, togHeight))
        self.onOffComp.SetFont(tog_font)
        self.onOffComp.Bind(wx.EVT_TOGGLEBUTTON, self.handleOnOffComp)
    
        self.knobComp1 = ControlKnob(self, -60, 0, -3, label='Threshold', backColour=colour, outFunction=self.changeComp1)
        self.knobComp1.SetPosition((12, 428))
        self.knobComp2 = ControlKnob(self, 1, 10, 2, label='Ratio', backColour=colour, outFunction=self.changeComp2)
        self.knobComp2.SetPosition((64, 428))
        self.knobComp3 = ControlKnob(self, 0.001, 0.5, 0.01, label='Risetime', backColour=colour, outFunction=self.changeComp3)
        self.knobComp3.SetPosition((116, 428))
        self.knobComp4 = ControlKnob(self, 0.01, 1, .1, label='Falltime', backColour=colour, outFunction=self.changeComp4)
        self.knobComp4.SetPosition((168, 428))
    
        if vars.constants["PLATFORM"] == "darwin":
            # reduce font for OSX display
            objs = [self.driverText, self.popupDriver, self.interfaceText, self.popupInterface, self.srText, self.popupSr, 
                    self.polyText, self.popupPoly, self.bitText, self.popupBit, self.formatText, self.popupFormat, 
                    self.onOffText, self.onOff, self.recText, self.rec, self.textAmp]
            font, psize = self.title.GetFont(), self.title.GetFont().GetPointSize()
            font.SetPointSize(psize-2)
            for obj in objs:
                obj.SetFont(font)
        elif vars.constants["PLATFORM"] == "linux2":
            # leave StaticText font as is on linux
            objs = [self.popupDriver, self.popupInterface, self.popupSr, 
                    self.popupPoly, self.popupBit, self.popupFormat, 
                    self.onOff, self.rec]
            font, psize = self.title.GetFont(), self.title.GetFont().GetPointSize()
            font.SetPointSize(psize-1)
            for obj in objs:
                obj.SetFont(font)
    
    def start(self):
        self.fsserver.start()
    
    def stop(self):
        self.fsserver.stop()
    
    def shutdown(self):
        self.fsserver.shutdown()
    
    def boot(self):
        self.fsserver.boot()
    
    def setAmpCallable(self):
        self.fsserver.setAmpCallable(self.meter)
    
    def setRecordOptions(self, dur, filename):
        fileformats = {"wav": 0, "aif": 1}
        if fileformats.has_key(self.fileformat):
            fileformat = fileformats[self.fileformat]
        else:
            fileformat = self.fileformat
        sampletypes = {16: 0, 24: 1, 32: 3}
        if sampletypes.has_key(self.sampletype):
            sampletype = sampletypes[self.sampletype]
        else:
            sampletype = self.sampletype
        self.fsserver.recordOptions(dur, filename, fileformat, sampletype)
    
    def reinitServer(self, sliderport, audio, serverSettings, postProcSettings):
        vars.vars["SLIDERPORT"] = sliderport
        self.fsserver.shutdown()
        self.fsserver.reinit(audio=audio)
        self.fsserver.boot()
        self.setServerSettings(serverSettings)
        self.setPostProcSettings(postProcSettings)
    
    def getExtensionFromFileFormat(self):
        return {0: "wav", 1: "aif"}.get(self.fileformat, "wav")
    
    def prepareForVirtualKeyboard(self):
        evt = wx.CommandEvent(10006, self.popupInterface.GetId())
        evt.SetInt(1)
        self.changeInterface(evt)
    
    def resetVirtualKeyboard(self):
        modules = self.GetTopLevelParent().modules
        for pit in self.virtualNotePressed.keys():
            voice = self.virtualNotePressed[pit]
            del self.virtualNotePressed[pit]
            for module in modules:
                synth = module.synth
                synth._virtualpit[voice].setValue(pit)
                synth._trigamp[voice].setValue(0)
        self.virtualvoice = 0
        self.keyboard.reset()
    
    def onKeyboard(self, note):
        pit = note[0]
        vel = note[1]
        if vel > 0 and pit not in self.virtualNotePressed.keys():
            for i in range(vars.vars["POLY"]):
                self.virtualvoice = (self.virtualvoice+1) % vars.vars["POLY"]
                if self.virtualvoice not in self.virtualNotePressed.values():
                    break
            voice = self.virtualNotePressed[pit] = self.virtualvoice
        elif vel == 0 and pit in self.virtualNotePressed.keys():
            voice = self.virtualNotePressed[pit]
            del self.virtualNotePressed[pit]
        modules = self.GetTopLevelParent().modules
        for module in modules:
            synth = module.synth
            synth._virtualpit[voice].setValue(pit)
            synth._trigamp[voice].setValue(vel / 127.)
    
    def handleAudio(self, evt):
        popups = [self.popupDriver, self.popupInterface, self.popupSr, self.popupPoly, self.popupBit, self.popupFormat]
        menuIds = [vars.constants["ID"]["New"], vars.constants["ID"]["Open"], vars.constants["ID"]["MidiLearn"], 
                   vars.constants["ID"]["Export"], vars.constants["ID"]["Quit"]]
        if evt.GetInt() == 1:
            for popup in popups:
                popup.Disable()
            for menuId in menuIds:
                self.GetTopLevelParent().menubar.FindItemById(menuId).Enable(False)
            self.fsserver.start()
        else:
            self.fsserver.stop()
            for popup in popups:
                if popup != self.popupDriver or vars.vars["AUDIO_HOST"] != "Jack":
                    popup.Enable()
            for menuId in menuIds:
                self.GetTopLevelParent().menubar.FindItemById(menuId).Enable(True)
    
    def handleRec(self, evt):
        if evt.GetInt() == 1:
            ext = self.getExtensionFromFileFormat()
            path = os.path.join(os.path.expanduser("~"), "Desktop", "zyne_live_rec.%s" % ext)
            self.setRecordOptions(dur=-1, filename=path)
            self.fsserver.recstart()
        else:
            self.fsserver.recstop()
    
    def changeAmp(self, value):
        self.fsserver.setAmp(math.pow(10.0, float(value) * 0.05))
    
    def getServerSettings(self):
        return [self.popupSr.GetSelection(), self.popupPoly.GetSelection(), self.popupBit.GetSelection(), 
                self.popupFormat.GetSelection(), self.sliderAmp.GetValue()]
    
    def getPostProcSettings(self):
        dic = {}
        dic["EQ"] = [self.onOffEq.GetValue(), self.knobEqF1.GetValue(), self.knobEqF2.GetValue(), self.knobEqF3.GetValue(),
                    self.knobEqA1.GetValue(), self.knobEqA2.GetValue(), self.knobEqA3.GetValue(), self.knobEqA4.GetValue()]
        dic["Comp"] = [self.onOffComp.GetValue(), self.knobComp1.GetValue(), self.knobComp2.GetValue(),
                    self.knobComp3.GetValue(), self.knobComp4.GetValue()]
        return dic
    
    def setServerSettings(self, serverSettings):
        popups = [self.popupSr, self.popupPoly, self.popupBit, self.popupFormat]
        self.setPoly(serverSettings[1]+1)
        for i, popup in enumerate(popups):
            val = serverSettings[i]
            popup.SetSelection(val)
            evt = wx.CommandEvent(10006, popup.GetId())
            evt.SetInt(val)
            popup.ProcessEvent(evt)
        amp = serverSettings[4]
        self.sliderAmp.SetValue(amp)
        self.sliderAmp.outFunction(amp)
        self.resetVirtualKeyboard()
    
    def setPostProcSettings(self, postProcSettings):
        eq = postProcSettings["EQ"]
        comp = postProcSettings["Comp"]
        widgets = [self.onOffEq, self.knobEqF1, self.knobEqF2, self.knobEqF3,
                    self.knobEqA1, self.knobEqA2, self.knobEqA3, self.knobEqA4]
        for i, widget in enumerate(widgets):
            if i == 0:
                val = eq[i]
                widget.SetValue(val)
                evt = wx.CommandEvent(10127, widget.GetId())
                evt.SetInt(val)
                widget.ProcessEvent(evt)
            else:
                widget.SetValue(eq[i])
                widget.outFunction(eq[i])
        widgets = [self.onOffComp, self.knobComp1, self.knobComp2, self.knobComp3, self.knobComp4]
        for i, widget in enumerate(widgets):
            if i == 0:
                val = comp[i]
                widget.SetValue(val)
                evt = wx.CommandEvent(10127, widget.GetId())
                evt.SetInt(val)
                widget.ProcessEvent(evt)
            else:
                widget.SetValue(comp[i])
                widget.outFunction(comp[i])
        
    def setDriverSetting(self, func=None, val=0):
        if vars.vars["VIRTUAL"]:
            self.resetVirtualKeyboard()
        modules, params, lfo_params, ctl_params = self.GetTopLevelParent().getModulesAndParams()
        self.GetTopLevelParent().deleteAllModules()
        self.fsserver.shutdown()
        if func != None: func(val)
        self.fsserver.boot()
        self.GetTopLevelParent().setModulesAndParams(modules, params, lfo_params, ctl_params)
    
    def changeDriver(self, evt):
        if vars.vars["AUDIO_HOST"] != "Jack":
            self.setDriverSetting(self.fsserver.setOutputDevice, self.driverIndexes[evt.GetInt()])
    
    def changeInterface(self, evt):
        mainFrame = self.GetTopLevelParent()
        mainFrameSize = mainFrame.GetSize()
        try:
            self.setDriverSetting(self.fsserver.setMidiInputDevice, self.interfaceIndexes[evt.GetInt()])
            vars.vars["VIRTUAL"] = False
            if self.keyboardShown:
                self.keyboardShown = 0
                self.keyboard.reset()
                mainFrame.SetSize((mainFrameSize[0], mainFrameSize[1]-80))
                mainFrame.showKeyboard(False)
        except IndexError:
            if not self.keyboardShown:
                vars.vars["VIRTUAL"] = True
                self.setDriverSetting()
                screenRect = self.GetTopLevelParent().GetScreenRect()
                self.keyboardShown = 1
                mainFrame.SetSize((mainFrameSize[0], mainFrameSize[1]+80))
                mainFrame.showKeyboard()
    
    def changeSr(self, evt):
        if evt.GetInt() == 0: sr = 44100
        elif evt.GetInt() == 1: sr = 48000
        else: sr = 96000
        self.setDriverSetting(self.fsserver.setSamplingRate, sr)
    
    def setPoly(self, poly):
        vars.vars["POLY"] = poly
        self.keyboard.setPoly(poly)
    
    def changePoly(self, evt):
        vars.vars["POLY"] = evt.GetInt() + 1
        self.keyboard.setPoly(vars.vars["POLY"])
        self.setDriverSetting()
    
    def changeBit(self, evt):
        if evt.GetString():
            self.sampletype = int(evt.GetString())
    
    def changeFormat(self, evt):
        self.fileformat = evt.GetInt()
    
    ### EQ controls ###
    def handleOnOffEq(self, evt):
        if evt.GetInt() == 1:
            self.onOffEq.SetLabel("Off")
            self.fsserver.onOffEq(1)
        else:
            self.onOffEq.SetLabel("On")
            self.fsserver.onOffEq(0)
    
    def changeEqF1(self, x):
        self.fsserver.setEqFreq(0, x)
    
    def changeEqF2(self, x):
        self.fsserver.setEqFreq(1, x)
    
    def changeEqF3(self, x):
        self.fsserver.setEqFreq(2, x)
    
    def changeEqA1(self, x):
        self.fsserver.setEqGain(0, math.pow(10.0, x * 0.05))
    
    def changeEqA2(self, x):
        self.fsserver.setEqGain(1, math.pow(10.0, x * 0.05))
    
    def changeEqA3(self, x):
        self.fsserver.setEqGain(2, math.pow(10.0, x * 0.05))
    
    def changeEqA4(self, x):
        self.fsserver.setEqGain(3, math.pow(10.0, x * 0.05))
    
    ### Compressor controls ###
    def handleOnOffComp(self, evt):
        if evt.GetInt() == 1:
            self.onOffComp.SetLabel("Off")
            self.fsserver.onOffComp(1)
        else:
            self.onOffComp.SetLabel("On")
            self.fsserver.onOffComp(0)
    
    def changeComp1(self, x):
        self.fsserver.setCompParam("thresh", x)
    
    def changeComp2(self, x):
        self.fsserver.setCompParam("ratio", x)
    
    def changeComp3(self, x):
        self.fsserver.setCompParam("risetime", x)
    
    def changeComp4(self, x):
        self.fsserver.setCompParam("falltime", x)
    
    def midiLearn(self, state):
        learnColour = "#EAC1C1"
        popups = [self.popupDriver, self.popupInterface, self.popupSr, self.popupPoly, self.popupBit, self.popupFormat, self.onOff, self.rec]
        widgets = [self.knobEqF1, self.knobEqF2, self.knobEqF3, self.knobEqA1, self.knobEqA2, 
                   self.knobEqA3, self.knobEqA4, self.knobComp1, self.knobComp2, self.knobComp3, self.knobComp4]
        if state:
            self.SetBackgroundColour(learnColour)
            self.Refresh()
            self.sliderAmp.setBackgroundColour(learnColour)
            self.sliderAmp.Refresh()
            for widget in widgets:
                widget.setbackColour(learnColour)
                widget.Refresh()
            for widget in popups:
                widget.Disable()
            self.GetTopLevelParent().menubar.FindItemById(vars.constants["ID"]["Run"]).Enable(False)
            self.fsserver.startMidiLearn()
        else:
            self.SetBackgroundColour(self.colour)
            self.Refresh()
            self.sliderAmp.setBackgroundColour(self.colour)
            self.sliderAmp.Refresh()
            for widget in widgets:
                widget.setbackColour(self.colour)
                widget.Refresh()
            for widget in popups:
                widget.Enable()
            self.GetTopLevelParent().menubar.FindItemById(vars.constants["ID"]["Run"]).Enable(True)
            self.fsserver.stopMidiLearn()
            self.setDriverSetting()

class BasePanel(wx.Panel):
    def __init__(self, parent, name, title, synth, p1, p2, p3, from_lfo=False):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        if from_lfo:
            self.name, self.synth = name, synth
        else:
            self.name, self.synth = name, synth([p1,p2,p3])
        self.SetMaxSize((230,250))
        self.SetBackgroundColour(BACKGROUND_COLOUR)
        self.from_lfo = from_lfo
        if not self.from_lfo:
            self.lfo_sliders = [get_lfo_init(), get_lfo_init(), get_lfo_init(), get_lfo_init()]
            self.buttons = [None, None, None, None]
            self.lfo_frames = [None, None, None, None]
        self.sliders = []
        self.labels = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.titleSizer = wx.FlexGridSizer(1, 3, 5, 5)
        self.titleSizer.AddGrowableCol(1)
        #self.titleSizer.SetFlexibleDirection(wx.HORIZONTAL)
        #self.titleSizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_NONE)
        self.titleSizer.SetMinSize((220, -1))
        self.close = GenStaticText(self, -1, label="X")
        self.close.SetBackgroundColour(BACKGROUND_COLOUR)
        self.close.Bind(wx.EVT_ENTER_WINDOW, self.hoverX)
        self.close.Bind(wx.EVT_LEAVE_WINDOW, self.leaveX)
        self.close.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
        if not self.from_lfo:
            self.close.SetToolTip(wx.ToolTip("Delete module"))
        else:
            self.close.SetToolTip(wx.ToolTip("Close window"))
        self.title = wx.StaticText(self, id=-1, label=vars.vars["toSysEncoding"](title))
        if from_lfo:
            bmp = wx.BitmapFromImage(MOVE.GetImage().Rescale(16, 16))
            self.corner = GenStaticBitmap(self, -1, bitmap=bmp, size=(16,16), style=wx.NO_BORDER)
            self.corner.SetToolTip(wx.ToolTip("Move window"))
        else:
            self.corner = GenStaticText(self, -1, label="mute")
            self.corner.Bind(wx.EVT_LEFT_DOWN, self.MouseDownCorner)
        self.corner.SetBackgroundColour(BACKGROUND_COLOUR)
        self.corner.Bind(wx.EVT_ENTER_WINDOW, self.hoverCorner)
        self.corner.Bind(wx.EVT_LEAVE_WINDOW, self.leaveCorner)
        if from_lfo:
            self.titleSizer.AddMany([(self.close, 0, wx.LEFT|wx.TOP, 2), (self.title, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, 2), (self.corner, 0, wx.RIGHT, 5)])
            self.sizer.Add(self.titleSizer, 0, wx.BOTTOM|wx.TOP, 2)
            self.sizer.Add(ZyneStaticLine(self, size=(226, 2)), 0, wx.BOTTOM, 3)
        else:
            self.titleSizer.AddMany([(self.close, 0, wx.LEFT, 3), (self.title, 0, wx.ALIGN_CENTER_HORIZONTAL, 0), (self.corner, 0, wx.RIGHT, 3)])
            self.sizer.Add(self.titleSizer, 0, wx.BOTTOM|wx.TOP, 3)
            self.sizer.Add(ZyneStaticLine(self, size=(230, 2)), 0, wx.BOTTOM, 3)
        self.createAdsrKnobs()
        if from_lfo:
            self.sliderAmp = self.createSlider("Amplitude", .1, 0, 1, False, False, self.changeAmp, -1)
        else:
            self.sliderAmp = self.createSlider("Amplitude", 1, 0.0001, 2, False, False, self.changeAmp, 0)
            self.tmp_amplitude = 1

        self.font = self.close.GetFont()
        if vars.constants["PLATFORM"] == "darwin":
            ptsize = self.font.GetPointSize()
            self.font.SetPointSize(ptsize - 2)
        self.close.SetFont(self.font)
        self.title.SetFont(self.font)
        self.corner.SetFont(self.font)
    
    def createAdsrKnobs(self):
        self.knobSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.knobDel = ControlKnob(self, 0, 30.0, 0, log=False, label='Delay', outFunction=self.changeDelay)
        self.knobSizer.Add(self.knobDel, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 0)
        self.knobAtt = ControlKnob(self, 0.001, 30.0, 0.001, log=True, label='Attack', outFunction=self.changeAttack)
        self.knobSizer.Add(self.knobAtt, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 0)
        self.knobDec = ControlKnob(self, 0.001, 30.0, 0.1, log=True, label='Decay', outFunction=self.changeDecay)
        self.knobSizer.Add(self.knobDec, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 0)
        self.knobSus = ControlKnob(self, 0.001, 1.0, 0.7, label='Sustain', outFunction=self.changeSustain)
        self.knobSizer.Add(self.knobSus, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 0)
        self.knobRel = ControlKnob(self, 0.001, 30.0, 1.0, log=True, label='Release', outFunction=self.changeRelease)
        self.knobSizer.Add(self.knobRel, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 0)
        self.sizer.Add(self.knobSizer, 0, wx.BOTTOM|wx.LEFT, 1)
        self.sliders.extend([self.knobDel, self.knobAtt, self.knobDec, self.knobSus, self.knobRel])
        if vars.constants["PLATFORM"] != "darwin":
            self.sizer.AddSpacer(3)
    
    def createSlider(self, label, value, minValue, maxValue, integer, log, callback, i=-1):
        text = wx.StaticText(self, id=-1, label=vars.vars["toSysEncoding"](label), size=(200,16))
        self.labels.append(text)
        if vars.constants["PLATFORM"] == "darwin":
            font, psize = text.GetFont(), text.GetFont().GetPointSize()
            font.SetPointSize(psize-2)
            text.SetFont(font)
        self.sizer.Add(text, 0, wx.LEFT, 5)
        if integer or self.from_lfo:
            slider = ZyneControlSlider(self, minValue, maxValue, value, size=(212,14), log=log, integer=integer, outFunction=callback)
            self.sizer.Add(slider, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        else:
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            slider = ZyneControlSlider(self, minValue, maxValue, value, size=(195,14), log=log, integer=integer, outFunction=callback)
            button = LFOButtons(self, synth=self.synth, which=i, callback=self.startLFO)
            lfo_frame = LFOFrame(self.GetTopLevelParent(), self.synth, label, i)
            self.buttons[i] = button
            self.lfo_frames[i] = lfo_frame
            hsizer.Add(slider, 0)
            hsizer.Add(button, 0, wx.LEFT|wx.TOP, 2)
            self.sizer.Add(hsizer, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        self.sliders.append(slider)
        return slider
    
    def hoverX(self, evt):
        font = self.close.GetFont()
        font.SetWeight(wx.BOLD)
        self.close.SetFont(font)
        self.close.SetForegroundColour("#555555")

    def leaveX(self, evt):
        self.close.SetFont(self.font)
        self.close.SetForegroundColour("#000000")

    def MouseDown(self, evt):
        del self.synth
        if not self.from_lfo:
            self.GetTopLevelParent().deleteModule(self)
            self.Destroy()
        else:
            win = self.GetTopLevelParent()
            win.Hide()

    def hoverCorner(self, evt):
        if hasattr(self, "mute"):
            if self.mute:
                col = "#555555"
            else:
                col = "#0000CC"
        else:
            col = "#555555"
        font = self.corner.GetFont()
        font.SetWeight(wx.BOLD)
        self.corner.SetFont(font)
        self.corner.SetForegroundColour(col)
    
    def leaveCorner(self, evt):
        if hasattr(self, "mute"):
            if self.mute:
                col = "#000000"
            else:
                col = "#0000EE"
        else:
            col = "#000000"
        self.corner.SetFont(self.font)
        self.corner.SetForegroundColour(col)

    def changeDelay(self, x):
        self.synth.amp.delay = x
    
    def changeAttack(self, x):
        self.synth.amp.attack = x
    
    def changeDecay(self, x):
        self.synth.amp.decay = x
    
    def changeSustain(self, x):
        self.synth.amp.sustain = x
    
    def changeRelease(self, x):
        self.synth.amp.release = x
    
    def changeAmp(self, x):
        self.synth._rawamp.value = x
   
    def setBackgroundColour(self, col):
        self.SetBackgroundColour(col)
        self.close.SetBackgroundColour(col)
        self.corner.SetBackgroundColour(col)
        for slider in self.sliders:
            try:
                slider.setBackgroundColour(col)
            except:
                slider.setbackColour(col)
        for but in self.buttons:
            if but != None:
                but.SetBackgroundColour(col)
        self.Refresh()

    def getLFOParams(self):
        lfo_params = []
        for i in range(len(self.buttons)):
            if self.buttons[i] == None:
                lfo_params.append(get_lfo_init())
            else:
                if self.lfo_frames[i].IsShown():
                    offset = self.GetTopLevelParent().GetPosition()
                    pos = self.lfo_frames[i].GetPosition()
                    shown = (pos[0] - offset[0], pos[1] - offset[1])
                else:
                    shown = False
                params, ctl_params = self.lfo_frames[i].get()
                lfo_params.append({"state": self.buttons[i].state, "params": params, 
                                   "ctl_params": ctl_params, "shown": shown})
        return lfo_params
    
    def startLFO(self, which, x):
        self.lfo_sliders[which]["state"] = x
        if which == 0:
            if not x:
                self.synth._lfo_amp.stop()
            else:
                self.synth._lfo_amp.play()
        else:
            self.synth._params[which].start_lfo(x)
    
    def reinitLFOS(self, lfo_param):
        self.lfo_sliders = lfo_param
        for i, lfo_conf in enumerate(self.lfo_sliders):
            if self.buttons[i] != None:
                state = lfo_conf["state"]
                self.startLFO(i, state)
                self.buttons[i].setState(state)
                if lfo_conf["shown"]:
                    offset = self.GetTopLevelParent().GetPosition()
                    pos = (lfo_conf["shown"][0] + offset[0], lfo_conf["shown"][1] + offset[1])
                    self.lfo_frames[i].SetPosition(pos)
                    self.lfo_frames[i].Show()
                params = lfo_conf["params"]
                ctl_params = lfo_conf["ctl_params"]
                self.lfo_frames[i].set(params, ctl_params)

    def generateUniform(self):
        for i, slider in enumerate(self.sliders):
            if i == 0:
                continue
            mini = slider.getMinValue()
            maxi = slider.getMaxValue()
            if slider.integer:
                val = random.randint(mini, maxi)
            else:
                if i == 5:
                    val = random.uniform(.25, 1.5)
                else:
                    val = random.uniform(mini, maxi)
            slider.SetValue(val)
            slider.outFunction(val)
        for i, button in enumerate(self.buttons):
            if button != None:
                state = random.choice([0,0,0,1])
                button.setState(state)
                button.Refresh()
                if state == 1:
                    for j, slider in enumerate(self.lfo_frames[i].panel.sliders):
                        if j == 0:
                            continue
                        mini = slider.getMinValue()
                        maxi = slider.getMaxValue()
                        if slider.integer:
                            val = random.randint(mini, maxi)
                        else:
                            if j == 6:
                                val = random.uniform(0, 1)
                                val **= 10.0
                                val *= (maxi - mini)
                                val += mini
                            else:
                                val = random.uniform(mini, maxi)
                        slider.SetValue(val)
                        slider.outFunction(val)

    def generateTriangular(self):
        for i, slider in enumerate(self.sliders):
            if i == 0:
                continue
            mini = slider.getMinValue()
            maxi = slider.getMaxValue()
            if slider.integer:
                v1 = random.randint(mini, maxi)
                v2 = random.randint(mini, maxi)
                val = (v1 + v2) / 2
            else:
                if i == 5:
                    val = random.triangular(.25, 1.5)
                elif i in [1, 2]:
                    val = random.triangular(0, 1)
                    val **= 10.0
                    val *= (maxi - mini)
                    val += mini
                else:
                    val = random.triangular(mini, maxi)
            slider.SetValue(val)
            slider.outFunction(val)
        for i, button in enumerate(self.buttons):
            if button != None:
                state = random.choice([0,0,0,1])
                button.setState(state)
                button.Refresh()
                if state == 1:
                    for j, slider in enumerate(self.lfo_frames[i].panel.sliders):
                        if j == 0:
                            continue
                        mini = slider.getMinValue()
                        maxi = slider.getMaxValue()
                        if slider.integer:
                            v1 = random.randint(mini, maxi)
                            v2 = random.randint(mini, maxi)
                            val = (v1 + v2) / 2
                        else:
                            if j == 6:
                                val = random.triangular(0, 1)
                                val **= 10.0
                                val *= (maxi - mini)
                                val += mini
                            else:
                                val = random.triangular(mini, maxi)
                        slider.SetValue(val)
                        slider.outFunction(val)

    def generateMinimum(self):
        for i, slider in enumerate(self.sliders):
            if i == 0:
                continue
            mini = slider.getMinValue()
            maxi = slider.getMaxValue()
            if slider.integer:
                val = min([random.randint(mini, maxi) for k in range(4)])
            else:
                if i == 5:
                    val = random.uniform(.25, 1.25)
                elif i in [1, 2]:
                    val = min([random.uniform(0, 1) for k in range(2)])
                    val **= 10.0
                    val *= (maxi - mini)
                    val += mini
                else:
                    val = min([random.uniform(mini, maxi) for k in range(4)])
            slider.SetValue(val)
            slider.outFunction(val)
        for i, button in enumerate(self.buttons):
            if button != None:
                state = random.choice([0,0,0,1])
                button.setState(state)
                button.Refresh()
                if state == 1:
                    for j, slider in enumerate(self.lfo_frames[i].panel.sliders):
                        if j == 0:
                            continue
                        mini = slider.getMinValue()
                        maxi = slider.getMaxValue()
                        if slider.integer:
                            val = min([random.randint(mini, maxi) for k in range(4)])
                        else:
                            if j == 5:
                                val = min([random.uniform(0, 1) for k in range(8)])
                                val **= 10.0
                                val *= (maxi - mini)
                                val += mini
                            else:
                                val = min([random.uniform(mini, maxi) for k in range(4)])
                        slider.SetValue(val)
                        slider.outFunction(val)

    def jitterize(self):
        for i, slider in enumerate(self.sliders):
            if i == 0:
                continue
            mini = slider.getMinValue()
            maxi = slider.getMaxValue()
            if not slider.integer:
                off = random.uniform(.96, 1.04)
                val = slider.GetValue() * off
                if val < mini: val = mini
                elif val > maxi: val = maxi 
                slider.SetValue(val)
                slider.outFunction(val)
        for i, button in enumerate(self.buttons):
            if button != None:
                if button.state:
                    for slider in self.lfo_frames[i].panel.sliders:
                        if j == 0:
                            continue
                        mini = slider.getMinValue()
                        maxi = slider.getMaxValue()
                        if slider.integer:
                            off = random.randint(-1, 1)
                            val = slider.GetValue() + off
                            if val < mini: val = mini
                            elif val > maxi: val = maxi 
                        else:
                            off = random.uniform(.95, 1.05)
                            val = slider.GetValue() * off
                            if val < mini: val = mini
                            elif val > maxi: val = maxi 
                        slider.SetValue(val)
                        slider.outFunction(val)

class GenericPanel(BasePanel):
    def __init__(self, parent, name, title, synth, p1, p2, p3):
        BasePanel.__init__(self, parent, name, title, synth, p1, p2, p3)
        self.mute = 1
        if p1[0] == "Transposition":
            self.sliderTranspo = self.createSlider(p1[0], p1[1], p1[2], p1[3], p1[4], p1[5], self.changeTranspo, 1)
        else:
            self.sliderP1 = self.createSlider(p1[0], p1[1], p1[2], p1[3], p1[4], p1[5], self.changeP1, 1)
        if p2[0] == "Transposition":
            self.sliderTranspo = self.createSlider(p2[0], p2[1], p2[2], p2[3], p2[4], p2[5], self.changeTranspo, 2)
        else:
            self.sliderP2 = self.createSlider(p2[0], p2[1], p2[2], p2[3], p2[4], p2[5], self.changeP2, 2)
        if p3[0] == "Transposition":
            self.sliderTranspo = self.createSlider(p3[0], p3[1], p3[2], p3[3], p3[4], p3[5], self.changeTranspo, 3)
        else:
            self.sliderP3 = self.createSlider(p3[0], p3[1], p3[2], p3[3], p3[4], p3[5], self.changeP3, 3)
        self.SetSizerAndFit(self.sizer)    
    
    def changeP1(self, x):
        self.synth.set(1, x)
    
    def changeP2(self, x):
        self.synth.set(2, x)
    
    def changeP3(self, x):
        self.synth.set(3, x)
    
    def changeTranspo(self, x):
        self.synth._transpo.value = x

    def MouseDownCorner(self, evt):
        if self.mute:
            self.mute = 0
            self.corner.SetForegroundColour("#0000EE")
            self.tmp_amplitude = self.sliderAmp.GetValue()
            self.synth._lfo_amp.stop()
            self.sliderAmp.SetValue(0.0001)
            self.sliderAmp.Disable()
        else:
            self.mute = 1
            self.corner.SetForegroundColour("#000000")
            self.synth._lfo_amp.play()
            self.sliderAmp.SetValue(self.tmp_amplitude)
            self.sliderAmp.Enable()
        self.Refresh()
    
    def setMute(self, mute):
        self.mute = mute
        if self.mute:
            self.corner.SetForegroundColour("#000000")
            self.synth._lfo_amp.play()
            self.sliderAmp.SetValue(self.tmp_amplitude)
        else:
            self.tmp_amplitude = self.sliderAmp.GetValue()
            self.corner.SetForegroundColour("#0000EE")
            self.synth._lfo_amp.stop()
            self.sliderAmp.SetValue(0.0001)
        
class LFOPanel(BasePanel):
    def __init__(self, parent, name, title, synth, p1, p2, p3, which):
        BasePanel.__init__(self, parent, name, title, synth, p1, p2, p3, from_lfo=True)
        self.which = which
        self.sliderP1 = self.createSlider(p1[0], p1[1], p1[2], p1[3], p1[4], p1[5], self.changeP1)
        self.sliderP2 = self.createSlider(p2[0], p2[1], p2[2], p2[3], p2[4], p2[5], self.changeP2)
        self.sliderP3 = self.createSlider(p3[0], p3[1], p3[2], p3[3], p3[4], p3[5], self.changeP3)
        self.SetSizerAndFit(self.sizer) 
    
    def changeP1(self, x):
        if self.which == 0:
            self.synth._params[self.which].setSpeed(x)
        else:
            self.synth._params[self.which].lfo.setSpeed(x)
    
    def changeP2(self, x):
        if self.which == 0:
            self.synth._params[self.which].setType(x)
        else:
            self.synth._params[self.which].lfo.setType(x)
        wave = {0: "Ramp", 1: "Sawtooth", 2: "Square", 3: "Triangle", 4: "Pulse", 5: "Bipolar Pulse", 6: "Sample and Hold", 7: "Modulated Sine"}[x]
        self.labels[2].SetLabel(vars.vars["ensureNFD"]("Waveform  -  %s" % wave))

    def changeP3(self, x):
        if self.which == 0:
            self.synth._params[self.which].setJitter(x)
        else:
            self.synth._params[self.which].lfo.setJitter(x)
    
    def changeDelay(self, x):
        if self.which == 0:
            self.synth.amp.delay = x
        else:
            self.synth._params[self.which].lfo.amp.delay = x

    def changeAttack(self, x):
        if self.which == 0:
            self.synth.amp.attack = x
        else:
            self.synth._params[self.which].lfo.amp.attack = x
    
    def changeDecay(self, x):
        if self.which == 0:
            self.synth.amp.decay = x
        else:
            self.synth._params[self.which].lfo.amp.decay = x
    
    def changeSustain(self, x):
        if self.which == 0:
            self.synth.amp.sustain = x
        else:
            self.synth._params[self.which].lfo.amp.sustain = x
    
    def changeRelease(self, x):
        if self.which == 0:
            self.synth.amp.release = x
        else:
            self.synth._params[self.which].lfo.amp.release = x
    
    def changeAmp(self, x):
        if self.which == 0:
            self.synth._params[self.which].setAmp(x)
        else:
            self.synth._params[self.which].lfo.setAmp(x)

