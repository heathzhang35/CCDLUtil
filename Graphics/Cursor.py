import wx

"""
Graphics for cursor control task
"""

class Cursor(wx.Frame):

    def __init__(self, **kwargs):
        """
        A wxpython cursor task

        params:
            - x_pos: x position (defaults to 100)
            - y_pos: y position (defaults to 100)
            - full_screen: if to use full screen, cannot be used together with width & height
            - screen_width: size of screen in pixels
            - screen_height: height of screen in pixels
            - cursor_radius: the radius of the cursor
            - pen_thickness: the thickness of crosshair
        """

    def _update_dim(self):
        self.width, self.height = self.GetSize()
        self.screenheight_half = self.height // 2
        self.screenwidth_half = self.width // 2

    def go_left():
        pass

    def go_right():
        pass
    
    def go_up():
        pass

    def go_down():
        pass


