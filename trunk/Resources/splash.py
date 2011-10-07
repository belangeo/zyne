#!/usr/bin/env python
# encoding: utf-8

import wx, sys, os

def GetRoundBitmap( w, h, r ):
    maskColor = wx.Color(0,0,0)
    shownColor = wx.Color(5,5,5)
    b = wx.EmptyBitmap(w,h)
    dc = wx.MemoryDC(b)
    dc.SetBrush(wx.Brush(maskColor))
    dc.DrawRectangle(0,0,w,h)
    dc.SetBrush(wx.Brush(shownColor))
    dc.SetPen(wx.Pen(shownColor))
    dc.DrawCircle(w/2,h/2,w/2)
    dc.SelectObject(wx.NullBitmap)
    b.SetMaskColour(maskColor)
    return b

def GetRoundShape( w, h, r ):
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
        w, h = self.bmp.GetWidth(), self.bmp.GetHeight()
        self.SetClientSize((w, h))

        if wx.Platform == "__WXGTK__":
            self.Bind(wx.EVT_WINDOW_CREATE, self.SetWindowShape)
        else:
            self.SetWindowShape()

        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)

        self.fc = wx.FutureCall(3000, self.OnClose)

        self.Center(wx.HORIZONTAL)
        if sys.platform == 'win32':
            self.Center(wx.VERTICAL)
            
        self.Show(True)
        
    def SetWindowShape(self, *evt):
        r = GetRoundShape(350,350,10)
        self.hasShape = self.SetShape(r)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0,0,True)
     
    def OnClose(self):
        self.mainframe.Show()
        self.Destroy()

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = ZyneSplashScreen(None, img="ZyneSplash.png")
    app.MainLoop()