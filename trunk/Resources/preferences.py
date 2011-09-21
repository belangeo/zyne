#!/usr/bin/env python
# encoding: utf-8
import wx, os
import Resources.variables as vars
from Resources.audio import get_output_devices, get_midi_input_devices

class PreferencesDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Zyne Preferences')
        
        self.paths = ["CUSTOM_MODULES_PATH", "EXPORT_PATH"]
        self.drivers = ["OUTPUT_DRIVER", "MIDI_INTERFACE"]
        self.ids = {"CUSTOM_MODULES_PATH": 10001, "EXPORT_PATH": 10002, "OUTPUT_DRIVER": 20001, "MIDI_INTERFACE": 20002}
        
        self.prefs = dict()
        self.checkForPreferencesFile()
        self.createWidgets()
 
    def createWidgets(self):
        btnSizer = wx.StdDialogButtonSizer()
        itemSizer = wx.FlexGridSizer(2,2,0,50)
        driverSizer = wx.BoxSizer(wx.VERTICAL)
        pathSizer = wx.BoxSizer(wx.VERTICAL)
        rowSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
    
        message = wx.StaticText(self, label="Changes will be applied on next launch.")
        mainSizer.Add(message, 0, wx.TOP|wx.LEFT, 10)
        font, entryfont, pointsize = message.GetFont(), message.GetFont(), message.GetFont().GetPointSize()
        
        font.SetWeight(wx.BOLD)
        if vars.constants["PLATFORM"] in ["win32", "linux2"]:
            entryfont.SetPointSize(pointsize-1)
        else:
            font.SetPointSize(pointsize-1)
            entryfont.SetPointSize(pointsize-2)

        if vars.constants["PLATFORM"] == "linux2":
            host_choices = ["Portaudio", "Jack"]
        elif vars.constants["PLATFORM"] == "darwin":
            if vars.constants["OSX_BUILD_WITH_JACK_SUPPORT"]:
                host_choices = ["Portaudio", "Coreaudio", "Jack"]
            else:
                host_choices = ["Portaudio", "Coreaudio"]
        else:
            host_choices = ["Portaudio"]
        host = self.prefs["AUDIO_HOST"]
        lbl = wx.StaticText(self, label=vars.constants["VAR_PREF_LABELS"]["AUDIO_HOST"])
        lbl.SetFont(font)
        driverSizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 10)
        cbo = wx.ComboBox(self, value=host ,size=(100,-1), choices=host_choices,
                                  style=wx.CB_DROPDOWN|wx.CB_READONLY, name="AUDIO_HOST")
        driverSizer.AddSpacer((-1,5))
        driverSizer.Add(cbo, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 8)
 
        for key in self.drivers:
            lbl = wx.StaticText(self, label=vars.constants["VAR_PREF_LABELS"][key])
            lbl.SetFont(font)
            driverSizer.Add(lbl, 0, wx.LEFT|wx.RIGHT, 10)
            ctrlSizer = wx.BoxSizer(wx.HORIZONTAL)
            txt = wx.TextCtrl(self, size=(360,-1), value=self.prefs[key], name=key)
            ctrlSizer.Add(txt, 0, wx.ALL|wx.EXPAND, 5)
            but = wx.Button(self, id=self.ids[key], label="Choose...")
            but.Bind(wx.EVT_BUTTON, self.getDriver, id=self.ids[key])
            ctrlSizer.Add(but, 0, wx.ALL, 5)            
            driverSizer.Add(ctrlSizer, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
 
        for key in vars.constants["VARIABLE_NAMES"]:
            val = self.prefs[key]
            if key not in self.paths and key not in self.drivers and key != "AUDIO_HOST":
                lbl = wx.StaticText(self, label=vars.constants["VAR_PREF_LABELS"][key])
                lbl.SetFont(font)
                itemSizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 10)
 
                if vars.constants["VAR_CHOICES"].has_key(key):
                    default = val
                    choices = vars.constants["VAR_CHOICES"][key]
                    cbo = wx.ComboBox(self, value=val,size=(100,-1), choices=choices,
                                  style=wx.CB_DROPDOWN|wx.CB_READONLY, name=key)
                    itemSizer.Add(cbo, 0, wx.ALL, 5)
                else:
                    txt = wx.TextCtrl(self, size=(100,-1), value=val, name=key)
                    itemSizer.Add(txt, 0, wx.ALL, 5)
 
        for key in self.paths:
            if key == "CUSTOM_MODULES_PATH": func = self.getFile
            elif key == "EXPORT_PATH": func = self.getPath
            lbl = wx.StaticText(self, label=vars.constants["VAR_PREF_LABELS"][key])
            lbl.SetFont(font)
            pathSizer.Add(lbl, 0, wx.LEFT|wx.RIGHT, 10)
            ctrlSizer = wx.BoxSizer(wx.HORIZONTAL)
            txt = wx.TextCtrl(self, size=(360,-1), value=self.prefs[key], name=key)
            txt.SetFont(entryfont)
            ctrlSizer.Add(txt, 0, wx.ALL|wx.EXPAND, 5)
            but = wx.Button(self, id=self.ids[key], label="Choose...")
            but.Bind(wx.EVT_BUTTON, func, id=self.ids[key])
            ctrlSizer.Add(but, 0, wx.ALL, 5)            
            pathSizer.Add(ctrlSizer, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
    
        saveBtn = wx.Button(self, wx.ID_OK, label="Save")
        saveBtn.SetDefault()
        saveBtn.Bind(wx.EVT_BUTTON, self.onSave)
        btnSizer.AddButton(saveBtn)
         
        cancelBtn = wx.Button(self, wx.ID_CANCEL)
        btnSizer.AddButton(cancelBtn)
        btnSizer.Realize()
 
        mainSizer.AddSpacer((-1,10))
        mainSizer.Add(driverSizer, 0, wx.EXPAND)
        mainSizer.AddSpacer((-1,5))
        mainSizer.Add(itemSizer, 0, wx.EXPAND)
        mainSizer.AddSpacer((-1,10))
        mainSizer.Add(pathSizer, 0, wx.EXPAND)
        mainSizer.Add(wx.StaticLine(self, size=(480,1)), 0, wx.TOP|wx.BOTTOM, 10)
        mainSizer.Add(btnSizer, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        self.SetSizer(mainSizer)
        self.SetClientSize(self.GetBestSize())

    def getDriver(self, evt):
        id = evt.GetId()
        for name in self.ids.keys():
            if self.ids[name] == id:
                break
        if name == "OUTPUT_DRIVER":
            driverList, driverIndexes = get_output_devices()
            msg = "Choose an output driver..."
        elif name == "MIDI_INTERFACE":
            driverList, driverIndexes = get_midi_input_devices()
            msg = "Choose a Midi interface..."
        widget = wx.FindWindowByName(name)
        dlg = wx.SingleChoiceDialog(self, message=msg, caption="Driver Selector", 
                                    choices=driverList, style=wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            selection = dlg.GetStringSelection()
            widget.SetValue(selection)
        else:
            pass
        dlg.Destroy()

    def getFile(self, evt):
        id = evt.GetId()
        for name in self.ids.keys():
            if self.ids[name] == id:
                break
        widget = wx.FindWindowByName(name)
        dlg = wx.FileDialog(self, message="Choose a file", defaultDir=os.path.expanduser("~"), 
            defaultFile="", wildcard="Python source (*.py)|*.py", style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            widget.SetValue(path)
        else:
            pass
        dlg.Destroy()

    def getPath(self, evt):
        id = evt.GetId()
        for name in self.ids.keys():
            if self.ids[name] == id:
                break
        widget = wx.FindWindowByName(name)
        dlg = wx.DirDialog(self, "Choose the directory where to save the exported samples", os.path.expanduser("~"), style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            widget.SetValue(path)
        else:
            pass
        dlg.Destroy()

    def checkForPreferencesFile(self):
        preffile = os.path.join(os.path.expanduser("~"), ".zynerc")
        if os.path.isfile(preffile):
            with open(preffile, "r") as f:
                lines = f.readlines()
                if not lines[0].startswith("### Zyne") or not vars.constants["VERSION"] in lines[0]:
                    print "Zyne preferences out-of-date, using default values."
                    lines = vars.constants["DEFAULT_PREFS"].splitlines()
        else:
            lines = vars.constants["DEFAULT_PREFS"].splitlines()
        for line in lines[1:]:
            line = line.strip()
            if line:
                sline = line.split("=")
                self.prefs[sline[0].strip()] = sline[1].strip()

    def onSave(self, event):
        preffile = os.path.join(os.path.expanduser("~"), ".zynerc")
        with open(preffile, "w") as f:
            f.write("### Zyne version %s preferences ###\n" % vars.constants["VERSION"])
            for name in vars.constants["VARIABLE_NAMES"]:
                widget = wx.FindWindowByName(name)
                if isinstance(widget, wx.ComboBox):
                    value = widget.GetValue()
                    choices = widget.GetItems()
                else:
                    value = widget.GetValue()
                f.write("%s = %s\n" % (name, value))
            f.write("LAST_SAVED = %s\n" % vars.vars["LAST_SAVED"])
        self.EndModal(0)

 
