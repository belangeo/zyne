#!/usr/bin/env python
# encoding: utf-8
import wx, os, sys
import Resources.variables as vars
from Resources.panels import *
from Resources.preferences import PreferencesDialog
import wx.richtext as rt
import Resources.audio as audio

class TutorialFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.fileMenu.Append(vars.constants["ID"]["CloseTut"], 'Close...\tCtrl+W', kind=wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onClose, id=vars.constants["ID"]["CloseTut"])
        self.menubar.Append(self.fileMenu, "&File")
        self.SetMenuBar(self.menubar)
    
        self.code = False
    
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)
        self.rtc.SetEditable(False)
        wx.CallAfter(self.rtc.SetFocus)
    
        self.rtc.Freeze()
        self.rtc.BeginSuppressUndo()
        self.rtc.BeginParagraphSpacing(0, 20)
        self.rtc.BeginBold()
        self.rtc.BeginFontSize(16)
        self.rtc.WriteText("Welcome to the tutorial on how to create a custom zyne module.")
        self.rtc.EndFontSize()
        self.rtc.EndBold()
        self.rtc.Newline()
        lines = audio.__doc__.splitlines(True)
        section_count = 1
        for line in lines:
            if line.count("----") == 2:
                self.rtc.BeginBold()
                self.rtc.BeginFontSize(16)
                self.rtc.WriteText("%i.%s" % (section_count, line.replace("----", "")))
                self.rtc.EndFontSize()
                self.rtc.EndBold()
                section_count += 1
            elif not self.code and line.startswith("class") or line.startswith("MODULES"):
                self.code = True
                self.rtc.BeginFontSize(12)
                self.rtc.BeginItalic()
                self.rtc.WriteText(line)                
            elif self.code and not line.startswith(" ") and not line.startswith("class") and not line.startswith("MODULES"):
                self.code = False
                self.rtc.EndItalic()
                self.rtc.EndFontSize()
                self.rtc.WriteText(line)                
            else:
                self.rtc.WriteText(line)                
        self.rtc.Newline()
        self.rtc.EndParagraphSpacing()
        self.rtc.EndSuppressUndo()
        self.rtc.Thaw()
    
    def onClose(self, evt):
        self.Destroy()

class SamplingDialog(wx.Dialog):
    def __init__(self, parent, title="Export Samples...", pos=wx.DefaultPosition, size=wx.DefaultSize):
        wx.Dialog.__init__(self, parent, id=1, title=title, pos=pos, size=size)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, -1, "Export settings for sampled sounds."), 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(wx.StaticText(self, -1, "Common file name :"), 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.filename = wx.TextCtrl(self, -1, "zyne", size=(80,-1))
        box.Add(self.filename, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
    
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(wx.StaticText(self, -1, "First:"), 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.first = wx.TextCtrl(self, -1, "0", size=(40,-1))
        box.Add(self.first, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        box.Add(wx.StaticText(self, -1, "Last:"), 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.last = wx.TextCtrl(self, -1, "128", size=(40,-1))
        box.Add(self.last, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        box.Add(wx.StaticText(self, -1, "Step:"), 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.step = wx.TextCtrl(self, -1, "1", size=(40,-1))
        box.Add(self.step, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
    
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(wx.StaticText(self, -1, "Noteon dur:"), 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.noteon = wx.TextCtrl(self, -1, "1", size=(50,-1))
        box.Add(self.noteon, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        box.Add(wx.StaticText(self, -1, "Release dur:"), 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.release = wx.TextCtrl(self, -1, "1", size=(50,-1))
        box.Add(self.release, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
    
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
    
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        sizer.Add(btnsizer, 0, wx.ALIGN_RIGHT|wx.ALL, 5)
        self.SetSizer(sizer)

class ZyneFrame(wx.Frame):
    def __init__(self, parent=None, title=u"Zyne Synth - Untitled", size=(920,522)):
        wx.Frame.__init__(self, parent, id=-1, title=title, size=size)
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.fileMenu.Append(vars.constants["ID"]["New"], 'New...\tCtrl+N', kind=wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onNew, id=vars.constants["ID"]["New"])
        self.fileMenu.Append(vars.constants["ID"]["Open"], 'Open...\tCtrl+O', kind=wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onOpen, id=vars.constants["ID"]["Open"])
        self.fileMenu.Append(vars.constants["ID"]["Save"], 'Save\tCtrl+S', kind=wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onSave, id=vars.constants["ID"]["Save"])
        self.fileMenu.Append(vars.constants["ID"]["SaveAs"], 'Save as...\tShift+Ctrl+S', kind=wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onSaveAs, id=vars.constants["ID"]["SaveAs"])
        self.fileMenu.Append(vars.constants["ID"]["Export"], 'Export as samples...\tCtrl+E', kind=wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onExport, id=vars.constants["ID"]["Export"])
        pref_item = self.fileMenu.Append(vars.constants["ID"]["Prefs"], 'Preferences...\tCtrl+,', 'Open Cecilia preferences pane', kind=wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onPreferences, id=vars.constants["ID"]["Prefs"])
        self.fileMenu.AppendSeparator()
        quit_item = self.fileMenu.Append(vars.constants["ID"]["Quit"], 'Quit\tCtrl+Q', kind=wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.onQuit, id=vars.constants["ID"]["Quit"])
        if wx.Platform=="__WXMAC__":
            wx.App.SetMacExitMenuItemId(quit_item.GetId())
            wx.App.SetMacPreferencesMenuItemId(pref_item.GetId())
        self.addMenu = wx.Menu()
        self.buildAddModuleMenu()
        helpMenu = wx.Menu()        
        helpItem = helpMenu.Append(vars.constants["ID"]["About"], '&About Zyne %s' % vars.constants["VERSION"], 'wxPython RULES!!!')
        wx.App.SetMacAboutMenuItemId(helpItem.GetId())
        self.Bind(wx.EVT_MENU, self.showAbout, helpItem)
        tuturialCreateModuleItem = helpMenu.Append(vars.constants["ID"]["Tutorial"], "How to create a custom module")
        self.Bind(wx.EVT_MENU, self.openTutorialCreateModule, tuturialCreateModuleItem)
    
        self.Bind(wx.EVT_CLOSE, self.onQuit)
        
        self.menubar.Append(self.fileMenu, "&File")
        self.menubar.Append(self.addMenu, "&Modules")
        self.menubar.Append(helpMenu, "&Help")
        self.SetMenuBar(self.menubar)
    
        if vars.constants["PLATFORM"] == "win32":
            self.SetMinSize((460, 554))
        elif vars.constants["PLATFORM"] == "darwin":
            self.SetMinSize((460, 522))
        else:
            self.SetMinSize((460, 520))
        self.Bind(wx.EVT_SIZE, self.OnSize)
    
        self.openedFile = ""
        self.modules = []
    
        self.splitWindow = wx.SplitterWindow(self, -1, style = wx.SP_LIVE_UPDATE|wx.SP_PERMIT_UNSPLIT)
        self.splitWindow.SetSashSize(0)
    
        self.sizer = wx.GridBagSizer(0,0)        
        self.panel = wx.Panel(self.splitWindow)
        self.serverPanel = ServerPanel(self.panel)
        self.sizer.Add(self.serverPanel, (0,0), (2,1))
        self.panel.SetSizer(self.sizer)
    
        self.keyboard = Keyboard(self.splitWindow, outFunction=self.serverPanel.onKeyboard)
        self.serverPanel.keyboard = self.keyboard
        self.serverPanel.setServerSettings(self.serverPanel.serverSettings)
    
        self.splitWindow.SetMinimumPaneSize(0)
        self.splitWindow.SplitHorizontally(self.panel, self.keyboard, -80)
        self.splitWindow.Unsplit(None)
    
        dropTarget = MyFileDropTarget(self.panel)
        self.panel.SetDropTarget(dropTarget)
        if vars.vars["AUTO_OPEN"] == 'Default':
            self.openfile(os.path.join(vars.constants["RESOURCES_PATH"], "default.zy"))
        elif vars.vars["AUTO_OPEN"] == 'Last Saved':
            path = vars.vars["LAST_SAVED"]
            try:
                self.openfile(path)
            except:
                pass
        self.Show()
    
    def updateAddModuleMenu(self, evt):
        for mod in MODULES.keys():
             if mod in vars.vars["EXTERNAL_MODULES"]:
                 del MODULES[mod]
        items = self.addMenu.GetMenuItems()
        for item in items:
            self.addMenu.DeleteItem(item)
        audio.checkForCustomModules()
        self.buildAddModuleMenu()
        modules, params, lfo_params = self.getModulesAndParams()
        self.deleteAllModules()
        self.setModulesAndParams(modules, params, lfo_params)
    
    def buildAddModuleMenu(self):
        self.moduleNames = sorted(MODULES.keys())
        id = vars.constants["ID"]["Modules"]
        for i, name in enumerate(self.moduleNames):
            self.addMenu.Append(id, 'Add %s module\tCtrl+%d' % (name, ((i+1)%10)), kind=wx.ITEM_NORMAL)
            self.Bind(wx.EVT_MENU, self.onAddModule, id=id)
            id += 1
        if vars.vars["EXTERNAL_MODULES"] != {}:
            self.addMenu.AppendSeparator()
            moduleNames = sorted(vars.vars["EXTERNAL_MODULES"].keys())
            for i, name in enumerate(moduleNames):
                self.addMenu.Append(id, 'Add %s module' % name, kind=wx.ITEM_NORMAL)
                self.Bind(wx.EVT_MENU, self.onAddModule, id=id)
                self.moduleNames.append(name)
                MODULES.update(vars.vars["EXTERNAL_MODULES"].items())
                id += 1
            self.addMenu.AppendSeparator()
            self.addMenu.Append(id, "Update Modules", kind=wx.ITEM_NORMAL)
            self.Bind(wx.EVT_MENU, self.updateAddModuleMenu, id=id)
    
    def openTutorialCreateModule(self, evt):
        win = TutorialFrame(self, -1, "Zyne tutorial", size=(700, 500), style=wx.DEFAULT_FRAME_STYLE)
        win.Show(True)
    
    def showKeyboard(self, state=True):
        if state:
            self.splitWindow.SplitHorizontally(self.panel, self.keyboard, -80)
            self.SetMinSize((460, 602))
        else:
            self.splitWindow.Unsplit()
            if vars.constants["PLATFORM"] == "win32":
                self.SetMinSize((460, 542))
                self.SetSize((-1, 554))
            elif vars.constants["PLATFORM"] == "darwin":
                self.SetMinSize((460, 522))
                self.SetSize((-1, 522))
            else:
                self.SetMinSize((460, 520))
                self.SetSize((-1, 520))
    
    def OnSize(self, evt):
        self.splitWindow.SetSashPosition(-80)
        self.setModulePostions()
        evt.Skip()
    
    def onPreferences(self, evt):
        dlg = PreferencesDialog()
        dlg.ShowModal()
        dlg.Destroy()
    
    def updateLastSavedInPreferencesFile(self, path):
        preffile = os.path.join(os.path.expanduser("~"), ".zynerc")
        if os.path.isfile(preffile):
            with open(preffile, "r") as f:
                lines = f.readlines()
                if not lines[0].startswith("### Zyne") or not vars.constants["VERSION"] in lines[0]:
                    return
            with open(preffile, "w") as f:
                for line in lines:
                    if "LAST_SAVED" in line:
                        f.write("LAST_SAVED = %s\n" % path)
                    else:
                        f.write(line)
    
    def onQuit(self, evt):
        try:
            self.serverPanel.keyboardFrame.Destroy()
        except:
            pass
        for win in wx.GetTopLevelWindows():
            win.Destroy()
        self.serverPanel.shutdown()
        self.Destroy()
        sys.exit()

    def onNew(self, evt):
        self.deleteAllModules()
        self.openedFile = ""
        self.SetTitle("Zyne Synth - Untitled")
    
    def onSave(self, evt):
        if self.openedFile != "":
            self.savefile(self.openedFile)
        else:
            self.onSaveAs(evt)
    
    def onSaveAs(self, evt):
        if self.openedFile != "":
            filename = os.path.split(self.openedFile)[1]
        else:
            filename = "zynesynth"    
        dlg = wx.FileDialog(self, "Save file as...", defaultFile=filename, style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path != "":
                self.savefile(path)
        dlg.Destroy()
    
    def onOpen(self, evt):
        wildcard = "Zyne files (*.zy)|*.zy"
        dlg = wx.FileDialog(self, "Choose Zyne Synth file...", wildcard=wildcard, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path != "":
                self.openfile(path)
        dlg.Destroy()
    
    def onExport(self, evt):
        dlg = SamplingDialog(self, size=(325,220))
        dlg.CenterOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            if vars.vars["EXPORT_PATH"] and os.path.isdir(vars.vars["EXPORT_PATH"]):
                rootpath = vars.vars["EXPORT_PATH"]
            else:
                rootpath = os.path.join(os.path.expanduser("~"), "Desktop", "zyne_export")
                if not os.path.isdir(rootpath):
                    os.mkdir(rootpath)
            filename = dlg.filename.GetValue()
            first = int(dlg.first.GetValue())
            last = int(dlg.last.GetValue())
            step = int(dlg.step.GetValue())
            vars.vars["NOTEONDUR"] = float(dlg.noteon.GetValue())
            duration = float(dlg.release.GetValue()) + vars.vars["NOTEONDUR"]
            ext = self.serverPanel.getExtensionFromFileFormat()
            modules, params, lfo_params = self.getModulesAndParams()
            serverSettings = self.serverPanel.getServerSettings()
            postProcSettings = self.serverPanel.getPostProcSettings()
            self.deleteAllModules()
            self.serverPanel.reinitServer(0.001, "offline", serverSettings, postProcSettings)
            for i in range(first,last,step):
                vars.vars["MIDIPITCH"] = i
                self.setModulesAndParams(modules, params, lfo_params)
                path = os.path.join(rootpath, "%03d-%s.%s" % (i,filename, ext))
                self.serverPanel.setRecordOptions(dur=duration, filename=path)
                self.serverPanel.start()
                self.deleteAllModules()
                self.serverPanel.shutdown()
                self.serverPanel.boot()
            self.serverPanel.reinitServer(0.05, vars.vars["AUDIO_HOST"], serverSettings, postProcSettings)
            vars.vars["MIDIPITCH"] = None
            self.serverPanel.setAmpCallable()
            self.setModulesAndParams(modules, params, lfo_params)
        dlg.Destroy()
    
    def getModulesAndParams(self):
        modules = [module.name for module in self.modules]
        params = [[slider.GetValue() for slider in module.sliders] for module in self.modules]
        lfo_params = [module.lfo_sliders for module in self.modules]
        return modules, params, lfo_params
    
    def setModulesAndParams(self, modules, params, lfo_params):
        ### Need to plug lfo_params ###
        for name in modules:
            dic = MODULES[name]
            self.modules.append(GenericPanel(self.panel, name, dic["title"], dic["synth"], dic["p1"], dic["p2"], dic["p3"]))
            self.addModule(self.modules[-1])
        for i, paramset in enumerate(params):
            for j, param in enumerate(paramset):
                slider = self.modules[i].sliders[j]
                slider.SetValue(param)
                slider.outFunction(param)
        for i, lfo_param in enumerate(lfo_params):
            self.modules[i].reinitLFOS(lfo_param)
        self.refresh()
    
    def savefile(self, filename):
        modules, params, lfo_params = self.getModulesAndParams()
        serverSettings = self.serverPanel.getServerSettings()
        postProcSettings = self.serverPanel.getPostProcSettings()
        dic = {"server": serverSettings, "postproc": postProcSettings, "modules": modules, "params": params, "lfo_params": lfo_params}
        with open(filename, "w") as f:
            f.write(str(dic))
        self.openedFile = filename
        self.SetTitle("Zyne Synth - " + os.path.split(filename)[1])
        self.updateLastSavedInPreferencesFile(filename)
    
    def openfile(self, filename):
        with open(filename, "r") as f: text = f.read()
        dic = eval(text)
        self.deleteAllModules()
        self.serverPanel.setServerSettings(dic["server"])
        if "postproc" in dic:
            self.serverPanel.setPostProcSettings(dic["postproc"])            
        self.setModulesAndParams(dic["modules"], dic["params"], dic["lfo_params"])
        if filename.endswith("default.zy"):
            self.openedFile = ""
        else:
            self.openedFile = filename
        self.SetTitle("Zyne Synth - " + os.path.split(filename)[1])
    
    def setModulePostions(self):
        w, h = self.GetSize()
        mw, mh = self.serverPanel.GetSize()
        cols = w / mw
        try:
            for i, mod in enumerate(self.modules):
                num = i + 1
                if num/cols != 0:
                    num += 1                    
                self.sizer.SetItemPosition(mod, (num/cols, num%cols))
        except:
            for i in range(len(self.modules)):
                mod = len(self.modules) - i - 1
                num = len(self.modules) - i
                if num/cols != 0:
                    num += 1                    
                self.sizer.SetItemPosition(self.modules[mod], (num/cols, num%cols))
    
    def onAddModule(self, evt):
        name = self.moduleNames[evt.GetId()-vars.constants["ID"]["Modules"]]
        dic = MODULES[name]
        self.modules.append(GenericPanel(self.panel, name, dic["title"], dic["synth"], dic["p1"], dic["p2"], dic["p3"]))
        self.addModule(self.modules[-1])
    
    def addModule(self, mod):
        w, h = self.GetSize()
        mw, mh = self.serverPanel.GetSize()
        cols = w / mw
        num = len(self.modules)
        self.refreshOutputSignal()
        if num/cols != 0:
            num += 1
        self.sizer.Add(mod, (num/cols, num%cols))
        self.refresh()
        
    def deleteModule(self, module):
        self.sizer.Remove(module)
        self.modules.remove(module)
        self.refreshOutputSignal()
        self.setModulePostions()
        self.refresh()    
    
    def deleteAllModules(self):
        for module in self.modules:
            self.sizer.Remove(module)
            module.Destroy()
        self.modules = []
        self.refreshOutputSignal()
        self.keyboard.reset()
        self.refresh()
    
    def refreshOutputSignal(self):
        if len(self.modules) == 0:
            out = 0.0
        else:
            for i,mod in enumerate(self.modules):
                if i == 0:
                    out = mod.synth.out
                else:
                    out = out + mod.synth.out
        self.serverPanel.fsserver._outSig.value = out
    
    def refresh(self):
        self.sizer.Layout()    
        self.Refresh()   
    
    def showAbout(self, evt):
        info = wx.AboutDialogInfo()
    
        description = "Zyne is a simple soft synthesizer allowing the " \
        "user to create original sounds and export samples bank.\n\n" \
        "Zyne is written with Python and " \
        "WxPython and uses pyo as its audio engine."
    
        info.Name = 'Zyne'
        info.Version = '%s' % vars.constants["VERSION"]
        info.Description = description
        info.Copyright = u'(C) 2011 Olivier Bélanger'
        wx.AboutBox(info)

class ZyneApp(wx.App):
    def OnInit(self):
        self.frame = ZyneFrame(None)
        self.frame.SetPosition((50,50))
        self.frame.Show()
        return True
    
    def MacOpenFile(self, filename):
        self.frame.openfile(filename)


if __name__ == '__main__':
    file = None
    if len(sys.argv) >= 2:
        file = sys.argv[1]
    
    app = ZyneApp(0)
    if file:
        app.frame.openfile(file)
    app.MainLoop()
