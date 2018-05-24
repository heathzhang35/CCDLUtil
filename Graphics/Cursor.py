import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import wx
import time
from Utility.Decorators import threaded

"""
Graphics for cursor control task
"""

class Cursor(wx.Frame):

    def __init__(self, **kwargs):
        """
        A wxpython cursor task

        params:
            - x_pos: window x position (defaults to 100)
            - y_pos: window y position (defaults to 100)
            - full_screen: if to use full screen, cannot be used together with width & height
            - screen_width: size of screen in pixels
            - screen_height: height of screen in pixels
            - cursor_radius: the radius of the cursor
        """
        no_resize = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        wx.Frame.__init__(self, None, title="Cursor Task", style=no_resize)
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
        else:
            self.width, self.height = self.GetSize()
        self.cursor_radius = kwargs.get("cursor_radius", 30)
        self.cursor_x = self.width // 2
        self.cursor_y = self.height // 2
        # background
        self.SetBackgroundColour("gray")
        self.Bind(wx.EVT_PAINT, self._repaint)
        self._repaint()

    def _repaint(self, event=None):
        dc = wx.ClientDC(self)
        dc.Clear()
        pen = wx.Pen('white')
        dc.SetPen(pen)
        # Draw Horizontal Crosshair
        dc.DrawCircle(self.cursor_x, self.cursor_y, self.cursor_radius)

    def go_left(self, delta):
        self.cursor_x -= delta
        self._repaint()

    def go_right(self, delta):
        self.cursor_x += delta
        self._repaint()
    
    def go_up(self, delta):
        self.cursor_y -= delta
        self._repaint()

    def go_down(self, delta):
        self.cursor_y += delta
        self._repaint()

### TESTING ###
@threaded(True)
def ani(frame):
    for i in range(10):
        time.sleep(2)
        if i % 2 == 0:
            frame.go_left(30)
        else:
            frame.go_right(30)


if __name__ == '__main__':
    app = wx.App(False)
    ch = Cursor(full_screen=True, cursor_radius=50)
    ani(ch)
    ch.Show()
    app.MainLoop()
