#!/usr/bin/env python
# encoding: utf-8

import wx, sys, os
import Resources.variables as vars

def GetRoundBitmap(w, h, r=10):
    maskColour = wx.Colour(0,0,0)
    shownColour = wx.Colour(5,5,5)
    b = wx.EmptyBitmap(w,h)
    dc = wx.MemoryDC(b)
    dc.SetBrush(wx.Brush(maskColour))
    dc.DrawRectangle(0,0,w,h)
    dc.SetBrush(wx.Brush(shownColour))
    dc.SetPen(wx.Pen(shownColour))
    dc.DrawCircle(w/2,h/2,w/2)
    dc.SelectObject(wx.NullBitmap)
    b.SetMaskColour(maskColour)
    return b

def GetRoundShape(w, h, r=10):
    return wx.RegionFromBitmap(GetRoundBitmap(w,h,r))

class ZyneSplashScreen(wx.Frame):
    def __init__(self, parent, img, mainframe):
        display = wx.Display(0)
        size = display.GetGeometry()[2:]
        wx.Frame.__init__(self, parent, -1, "", pos=(-1, size[1]/6),
                         style = wx.FRAME_SHAPED | wx.SIMPLE_BORDER | wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        self.mainframe = mainframe
        self.bmp = wx.Bitmap(os.path.join(img), wx.BITMAP_TYPE_PNG)
        self.w, self.h = self.bmp.GetWidth(), self.bmp.GetHeight()
        self.SetClientSize((self.w, self.h))

        if wx.Platform == "__WXGTK__":
            self.Bind(wx.EVT_WINDOW_CREATE, self.SetWindowShape)
        else:
            self.SetWindowShape()

        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)

        self.fc = wx.FutureCall(3500, self.OnClose)

        self.Center(wx.HORIZONTAL)
        if sys.platform == 'win32':
            self.Center(wx.VERTICAL)
            
        wx.CallAfter(self.Show)
        
    def SetWindowShape(self, *evt):
        r = GetRoundShape(self.w, self.h)
        self.hasShape = self.SetShape(r)

    def OnPaint(self, evt):
        w,h = self.GetSize()
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen("#000000"))
        dc.SetBrush(wx.Brush("#000000"))
        dc.DrawRectangle(0,0,w,h)
        dc.DrawBitmap(self.bmp, 0,0,True)
        dc.SetTextForeground("#000000")
        font = dc.GetFont()
        ptsize = font.GetPointSize()
        if vars.constants["PLATFORM"] == "win32":
            pass
        else:
            font.SetFaceName("Monaco")
            font.SetPointSize(ptsize+3)
        dc.SetFont(font)
        dc.DrawLabel("Modular Soft Synthesizer", wx.Rect(20, 230, 400, 18), wx.ALIGN_LEFT)
        if vars.constants["PLATFORM"] == "win32":
            pass
        else:
            font.SetPointSize(ptsize+1)
        dc.SetFont(font)
        dc.DrawLabel(u"Olivier Bélanger", wx.Rect(0, 345, 400, 15), wx.ALIGN_CENTER)
        dc.DrawLabel("iACT, %s" % vars.constants["YEAR"], wx.Rect(0, 360, 400, 15), wx.ALIGN_CENTER)
        dc.DrawLabel("v. %s" % vars.constants["VERSION"], wx.Rect(0, 375, 400, 15), wx.ALIGN_CENTER)
     
    def OnClose(self):
        self.mainframe.Show()
        self.Destroy()

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = ZyneSplashScreen(None, img="ZyneSplash.png")
    app.MainLoop()