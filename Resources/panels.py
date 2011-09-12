# encoding: utf-8
import wx, os, math, copy
from wx.lib.stattext import GenStaticText
import Resources.variables as vars
from Resources.widgets import *
from pyolib._wxwidgets import VuMeter, ControlSlider, BACKGROUND_COLOUR
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
            "Phaser": { "title": "--- Phasing Synthesis ---", "synth": PhaserSynth, 
                    "p1": ["Spread", 1.1, .25, 2, False, False],
                    "p2": ["Bandwidth", .1, .001, 1, False, True],
                    "p3": ["Feedback", .95, .9, 1, False, False]
                    },
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
                    "p3": ["LFO Frequency", 1, .02, 20, False, True],
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
            "PluckedString": { "title": "--- Plucked String Synthesis ---", "synth": PluckedString, 
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
                "p1": ["Speed", 4, .01, 100, False, True],
                "p2": ["Waveform", 3, 0, 7, True, False],
                "p3": ["Jitter", 0, 0, 1, False, False]
                }

LFO_INIT = {"state": False, "params": [.001, .1, .7, 1, .1, 4, 3, 0]}
def get_lfo_init():
    return copy.deepcopy(LFO_INIT)

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
    
    def OnDropFiles(self, x, y, filename):
        self.window.GetTopLevelParent().openfile(filename[0])

class LFOFrame(wx.MiniFrame):
    def __init__(self, parent, synth, which):
        wx.MiniFrame.__init__(self, parent, -1, style=wx.NO_BORDER)
        self.SetMaxSize((230,250))
        self.SetBackgroundColour(BACKGROUND_COLOUR)
        self.which = which
        self.panel = LFOPanel(self, "LFO", "--- LFO controls ---", synth, LFO_CONFIG["p1"], LFO_CONFIG["p2"], LFO_CONFIG["p3"], which)
        self.panel.SetPosition((0,0))
        pos = wx.GetMousePosition()
        self.SetPosition((pos[0]+10, pos[1]+10))
    
    def get(self):
        params = [slider.GetValue() for slider in self.panel.sliders]
        return params
    
    def set(self, params):
        for i, p in enumerate(params):
            slider = self.panel.sliders[i]
            slider.SetValue(p)
            slider.outFunction(p)

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
        self.font.SetWeight(wx.BOLD)
        if vars.constants["PLATFORM"] != "darwin":
            self.font.SetPointSize(psize-2)
        else:
            self.font.SetPointSize(psize-4)
        self.SetFont(self.font)
        self.Bind(wx.EVT_ENTER_WINDOW, self.hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.leave)
        self.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
    
    def setState(self, state):
        self.state = state
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
            self.parent.lfo_frames[self.which].Show()
            return
        if self.state:
            self.state = False
            self.SetForegroundColour("#000000")
        else:
            self.state = True
            self.SetForegroundColour("#0000EE")
        self.callback(self.which, self.state)

class ServerPanel(wx.Panel):
    def __init__(self, parent, colour="#DDDDE7"):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
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
        self.sliderAmp = ControlSlider(self, -60, 18, 0, pos=(15,200), outFunction=self.changeAmp, backColour=colour)
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
        self.fsserver.recordOptions(dur=dur, filename=filename,
                                   fileformat=self.fileformat,
                                   sampletype=self.sampletype)
    
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
        menuIds = [vars.constants["ID"]["New"], vars.constants["ID"]["Open"], 
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
            path = os.path.join(os.path.expanduser("~"), "Desktop", "funnysynth.%s" % ext)
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
        modules, params, lfo_params = self.GetTopLevelParent().getModulesAndParams()
        self.GetTopLevelParent().deleteAllModules()
        self.fsserver.shutdown()
        if func != None: func(val)
        self.fsserver.boot()
        self.GetTopLevelParent().setModulesAndParams(modules, params, lfo_params)
    
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
        bit = evt.GetInt()
        if bit == 2: bit = 3
        self.sampletype = bit
    
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
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.titleSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.close = GenStaticText(self, -1, label="X")
        self.close.SetBackgroundColour(BACKGROUND_COLOUR)
        self.closeFont = self.close.GetFont()
        self.closeFont.SetWeight(wx.BOLD)
        self.close.SetFont(self.closeFont)
        self.close.Bind(wx.EVT_ENTER_WINDOW, self.hoverX)
        self.close.Bind(wx.EVT_LEAVE_WINDOW, self.leaveX)
        self.close.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
        self.titleSizer.Add(self.close, 0, wx.LEFT, 5)
        self.title = wx.StaticText(self, id=-1, label=title)
        off = (210 - self.title.GetSize()[0]) / 2
        self.titleSizer.Add(self.title, 0, wx.LEFT, off)
        self.sizer.Add(self.titleSizer, 0, wx.BOTTOM|wx.TOP, 4)
        self.createAdsrKnobs()
        if from_lfo:
            self.sliderAmp = self.createSlider("Amplitude", .1, 0, 1, False, False, self.changeAmp, -1)
        else:
            self.sliderAmp = self.createSlider("Amplitude", 1, 0, 2, False, False, self.changeAmp, 3)
    
    def createAdsrKnobs(self):
        self.knobSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.knobAtt = ControlKnob(self, 0.001, 10.0, 0.001, label='Attack', outFunction=self.changeAttack)
        self.knobSizer.Add(self.knobAtt, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 3)
        self.knobDec = ControlKnob(self, 0.001, 10.0, 0.1, label='Decay', outFunction=self.changeDecay)
        self.knobSizer.Add(self.knobDec, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 3)
        self.knobSus = ControlKnob(self, 0.001, 1.0, 0.7, label='Sustain', outFunction=self.changeSustain)
        self.knobSizer.Add(self.knobSus, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 3)
        self.knobRel = ControlKnob(self, 0.001, 10.0, 1.0, label='Release', outFunction=self.changeRelease)
        self.knobSizer.Add(self.knobRel, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 3)
        self.sizer.Add(self.knobSizer, 0, wx.BOTTOM|wx.LEFT, 1)
        self.sliders.extend([self.knobAtt, self.knobDec, self.knobSus, self.knobRel])
        if vars.constants["PLATFORM"] != "darwin":
            self.sizer.AddSpacer(3)
    
    def createSlider(self, label, value, minValue, maxValue, integer, log, callback, i=-1):
        text = wx.StaticText(self, id=-1, label=label, size=(200,16))
        if vars.constants["PLATFORM"] == "darwin":
            font, psize = text.GetFont(), text.GetFont().GetPointSize()
            font.SetPointSize(psize-2)
            text.SetFont(font)
        self.sizer.Add(text, 0, wx.LEFT, 5)
        if integer or self.from_lfo:
            slider = ControlSlider(self, minValue, maxValue, value, size=(216,16), log=log, integer=integer, outFunction=callback)
            self.sizer.Add(slider, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        else:
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            slider = ControlSlider(self, minValue, maxValue, value, size=(195,16), log=log, integer=integer, outFunction=callback)
            button = LFOButtons(self, synth=self.synth, which=i, callback=self.startLFO)
            lfo_frame = LFOFrame(None, self.synth, i)
            self.buttons[i] = button
            self.lfo_frames[i] = lfo_frame
            hsizer.Add(slider, 0)
            hsizer.Add(button, 0, wx.LEFT|wx.TOP, 2)
            self.sizer.Add(hsizer, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        self.sliders.append(slider)
        return slider
    
    def hoverX(self, evt):
        font, ptsize = self.close.GetFont(), self.close.GetFont().GetPointSize()
        font.SetPointSize(ptsize+2)
        self.close.SetFont(font)
        self.close.SetForegroundColour("#555555")
    
    def leaveX(self, evt):
        self.close.SetFont(self.closeFont)
        self.close.SetForegroundColour("#000000")
    
    def MouseDown(self, evt):
        del self.synth
        if not self.from_lfo:
            self.GetTopLevelParent().deleteModule(self)
            self.Destroy()
        else:
            win = self.GetTopLevelParent()
            win.Hide()
    
    def changeAttack(self, x):
        self.synth.amp.attack = x
    
    def changeDecay(self, x):
        self.synth.amp.decay = x
    
    def changeSustain(self, x):
        self.synth.amp.sustain = x
    
    def changeRelease(self, x):
        self.synth.amp.release = x
    
    def changeAmp(self, x):
        self.synth.amp.mul = x
    
    def getLFOParams(self):
        lfo_params = []
        for i in range(len(self.buttons)):
            if self.buttons[i] == None:
                lfo_params.append(get_lfo_init())
            else:
                lfo_params.append({"state": self.buttons[i].state, "params": self.lfo_frames[i].get()})
        return lfo_params
    
    def startLFO(self, which, x):
        self.lfo_sliders[which]["state"] = x
        if which == 3:
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
                params = lfo_conf["params"]
                self.lfo_frames[i].set(params)

class GenericPanel(BasePanel):
    def __init__(self, parent, name, title, synth, p1, p2, p3):
        BasePanel.__init__(self, parent, name, title, synth, p1, p2, p3)
        if p1[0] == "Transposition":
            self.sliderTranspo = self.createSlider(p1[0], p1[1], p1[2], p1[3], p1[4], p1[5], self.changeTranspo, 0)
        else:
            self.sliderP1 = self.createSlider(p1[0], p1[1], p1[2], p1[3], p1[4], p1[5], self.changeP1, 0)
        if p2[0] == "Transposition":
            self.sliderTranspo = self.createSlider(p2[0], p2[1], p2[2], p2[3], p2[4], p2[5], self.changeTranspo, 1)
        else:
            self.sliderP2 = self.createSlider(p2[0], p2[1], p2[2], p2[3], p2[4], p2[5], self.changeP2, 1)
        if p3[0] == "Transposition":
            self.sliderTranspo = self.createSlider(p3[0], p3[1], p3[2], p3[3], p3[4], p3[5], self.changeTranspo, 2)
        else:
            self.sliderP3 = self.createSlider(p3[0], p3[1], p3[2], p3[3], p3[4], p3[5], self.changeP3, 2)
        self.SetSizerAndFit(self.sizer)    
    
    def changeP1(self, x):
        self.synth.set(0, x)
    
    def changeP2(self, x):
        self.synth.set(1, x)
    
    def changeP3(self, x):
        self.synth.set(2, x)
    
    def changeTranspo(self, x):
        self.synth._transpo.value = x

class LFOPanel(BasePanel):
    def __init__(self, parent, name, title, synth, p1, p2, p3, which):
        BasePanel.__init__(self, parent, name, title, synth, p1, p2, p3, from_lfo=True)
        self.which = which
        self.sliderP1 = self.createSlider(p1[0], p1[1], p1[2], p1[3], p1[4], p1[5], self.changeP1)
        self.sliderP2 = self.createSlider(p2[0], p2[1], p2[2], p2[3], p2[4], p2[5], self.changeP2)
        self.sliderP3 = self.createSlider(p3[0], p3[1], p3[2], p3[3], p3[4], p3[5], self.changeP3)
        self.SetSizerAndFit(self.sizer) 
    
    def changeP1(self, x):
        if self.which == 3:
            self.synth._params[self.which].setSpeed(x)
        else:
            self.synth._params[self.which].lfo.setSpeed(x)
    
    def changeP2(self, x):
        if self.which == 3:
            self.synth._params[self.which].setType(x)
        else:
            self.synth._params[self.which].lfo.setType(x)
    
    def changeP3(self, x):
        if self.which == 3:
            self.synth._params[self.which].setJitter(x)
        else:
            self.synth._params[self.which].lfo.setJitter(x)
    
    def changeAttack(self, x):
        if self.which == 3:
            self.synth.amp.attack = x
        else:
            self.synth._params[self.which].lfo.amp.attack = x
    
    def changeDecay(self, x):
        if self.which == 3:
            self.synth.amp.decay = x
        else:
            self.synth._params[self.which].lfo.amp.decay = x
    
    def changeSustain(self, x):
        if self.which == 3:
            self.synth.amp.sustain = x
        else:
            self.synth._params[self.which].lfo.amp.sustain = x
    
    def changeRelease(self, x):
        if self.which == 3:
            self.synth.amp.release = x
        else:
            self.synth._params[self.which].lfo.amp.release = x
    
    def changeAmp(self, x):
        if self.which == 3:
            self.synth._params[self.which].setAmp(x)
        else:
            self.synth._params[self.which].lfo.setAmp(x)
