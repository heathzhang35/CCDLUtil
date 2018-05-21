"""
A crosshair, using wxPython
"""

import wx
import time


class Crosshair(wx.Frame):

    def __init__(self, **kwargs):
        """
        A wxpython Crosshair that can flash red.

        params:
            - x_pos: window x position (defaults to 100)
            - y_pos: window y position (defaults to 100)
            - full_screen: if to use full screen, cannot be used together with width & height
            - screen_width: size of screen in pixels
            - screen_height: height of screen in pixels
            - crosshair_width: the size of crosshair
            - pen_thickness: the thickness of crosshair
        """
        wx.Frame.__init__(self, None, title="Crosshair")
        # go full screen?
        full_screen = kwargs.get("full_screen", False) 
        self.ShowFullScreen(full_screen)
        if full_screen and ("screen_width" in kwargs or "screen_height" in kwargs):
            raise ValueError("Cannot use full screen and define width.height together!")
        if not full_screen:
            self.SetPosition((kwargs.get("x_pos", 100), kwargs.get("y_pos", 100)))
        self.width = kwargs.get("screen_width", 500) 
        self.height = kwargs.get("screen_height", 500) 
        if not full_screen:
            self.SetSize((self.width, self.height))
        # some dependency
        self.crosshair_width = kwargs.get("crosshair_width", 30)  
        self.width_half = self.crosshair_width // 2
        self.height_half = self.width_half
        self.thickness = kwargs.get("pen_thickness", 5)
        self.pen_color = wx.WHITE
        self._update_dim()
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def _update_dim(self):
        self.width, self.height = self.GetSize()
        self.screenheight_half = self.height // 2
        self.screenwidth_half = self.width // 2

    def OnPaint(self, event=None):
        """
        Redraws the crosshair with the current pen color
        """
        self._update_dim()
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.SetPen(wx.Pen(self.pen_color, self.thickness))
        # Draw Horizontal Crosshair
        dc.DrawLine(self.screenwidth_half - self.width_half, self.screenheight_half,
                    self.screenwidth_half + self.width_half, self.screenheight_half)
        # Draw Horizontal Crosshair
        dc.DrawLine(self.screenwidth_half, self.screenheight_half - self.height_half,
                    self.screenwidth_half, self.screenheight_half + self.height_half)

    def flash_red(self, duration=0.2):
        """
        Causes the crosshair to flash red for duration seconds.
        :param duration: duration in seconds. defaults to 0.2
        """
        self.pen_color = wx.RED
        self.Refresh(True)
        t = time.time()
        while time.time() - t < duration:
            time.sleep(0.001)
        self.pen_color = wx.WHITE
        self.Refresh(True)


if __name__ == '__main__':
    app = wx.App(False)
    ch = Crosshair(full_screen=True)
    ch.Show()
    app.MainLoop()
