import wx
import numpy as np
from SimpleTetrisModel import GameModel
import time
from CCDLUtil.Utility.Decorators import threaded


class GameView(wx.Panel):

    def __init__(self, parent):
        # init parent
        super(GameView, self).__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.Colour(128, 128, 128))
        # bind to call
        self.Bind(wx.EVT_SIZE, self._refresh)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        # flags for drawing on canvas
        self._draw_crosshair = False
        self._crosshair_size = 20
        self._draw_cursortask = False
        # if not initialized, use the center of screen
        self._cursor_pos = None
        self._draw_text = False
        self._text = None
        self._text_pos = None

        # game model
        self._game_model = GameModel(12, 8)

    def _refresh(self, event):
        """Refresh canvas
        """
        event.Skip()
        self.Refresh()

    def _on_paint(self, event):
        # get width and height
        w, h = self.GetClientSize()
        # initialize cursor position
        # get the pen
        dc = wx.AutoBufferedPaintDC(self)
        # clear everything, and then redraw
        dc.Clear()
        if self._draw_crosshair:
            self._paint_crosshair(dc, w, h, size=self._crosshair_size)

        if self._draw_cursortask:
            self._paint_cursortask(dc, w, h)
            self._paint_cursor(dc, w, h, self._cursor_pos)

        if self._draw_text:
            self._paint_text(dc, self._text, pos=self._text_pos)

        self._paint_tetris(dc, w, h)

    def show_crosshair(self, size=20):
        self._draw_crosshair = True
        self._crosshair_size = size
        self.Refresh()

    def hide_crosshair(self):
        self._draw_crosshair = False
        self.Refresh()

    def show_cursortask(self, size=30):
        self._draw_cursortask = True
        self._crosshair_size = size
        self.Refresh()

    def hide_cursortask(self):
        self._draw_cursortask = False
        self.Refresh()

    def move_cursor(self, delta_x):
        """Move the cursor by delta_x distance

        :param delta_x: move by delta_x. Move to the right if delta_x is positive, else move to the left
        """
        if self._cursor_pos is None:
            w, _ = self.GetClientSize()
            self._cursor_pos = w / 2
        self._cursor_pos += delta_x
        self.Refresh()

    def show_text(self, text, pos):
        """Show text at certain position

        :param text: the text to show
        :param pos: the position to show text in form (x, y)
        """
        self._draw_text = True
        self._text = text
        self._text_pos = pos
        self.Refresh()

    def _paint_crosshair(self, dc, w, h, size):
        # draw crosshair
        dc.SetPen(wx.Pen(wx.BLACK, 5))
        dc.DrawLine(w / 2 - size, h / 2, w / 2 + size, h / 2)
        dc.DrawLine(w / 2, h / 2 - size, w / 2, h / 2 + size)

    def _paint_cursortask(self, dc, w, h):
        # draw cursortask
        width = w / 8
        dc.SetPen(wx.Pen("green"))
        dc.SetBrush(wx.Brush("green"))
        dc.DrawRectangle(0, 0, width, h)
        dc.DrawRectangle(w - width, 0, width, h)
        dc.SetPen(wx.Pen("black"))
        font = wx.Font(36, wx.ROMAN, wx.BOLD, wx.NORMAL)
        dc.SetFont(font)
        text_w, text_h = dc.GetTextExtent("YES")
        dc.DrawText("YES", width / 2 - text_w / 2, h / 2 - text_h / 2)
        text_w, text_h = dc.GetTextExtent("NO")
        dc.DrawText("NO", w - width / 2 - text_w / 2, h / 2 - text_h / 2)

    def _paint_cursor(self, dc, w, h, pos=None):
        if pos is None:
            pos = w / 2
        size = w / 30
        dc.SetPen(wx.Pen("White"))
        dc.SetBrush(wx.Brush("White"))
        dc.DrawCircle(pos, h / 2, size)

    def _paint_text(self, dc, text, pos=None):
        if pos is None:
            pos = self.GetClientSize()
            pos = (pos[0] / 2, pos[1] / 6)
        font = wx.Font(36, wx.ROMAN, wx.BOLD, wx.NORMAL)
        dc.SetFont(font)
        dc.SetPen(wx.Pen("Black"))
        text_w, text_h = dc.GetTextExtent(text)
        dc.DrawText(text, pos[0] - text_w / 2, pos[1] - text_h / 2)


    def _draw_square(self, dc, x, y, size):

        colors = ['#000000', '#CC6666', '#66CC66', '#6666CC',
                  '#CCCC66', '#CC66CC', '#66CCCC', '#DAAA00']

        light = ['#000000', '#F89FAB', '#79FC79', '#7979FC',
                 '#FCFC79', '#FC79FC', '#79FCFC', '#FCC600']

        dark = ['#000000', '#803C3B', '#3B803B', '#3B3B80',
                '#80803B', '#803B80', '#3B8080', '#806200']

        # pen = wx.Pen(light[2])
        # pen.SetCap(wx.CAP_PROJECTING)
        # dc.SetPen(pen)

        # dc.DrawLine(x, y + size - 1, x, y)
        # dc.DrawLine(x, y, x + size - 1, y)

        # darkpen = wx.Pen(dark[2])
        # darkpen.SetCap(wx.CAP_PROJECTING)
        # dc.SetPen(darkpen)

        # dc.DrawLine(x + 1, y + size - 1, x + size - 1, y + size - 1)
        # dc.DrawLine(x + size - 1, y + size - 1, x + size - 1, y + 1)

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(colors[2]))
        dc.DrawRectangle(x, y, size - 10, size - 10)

    def _paint_tetris(self, dc, w, h):
        num_rows, num_cols = self._game_model.get_size()
        x_coors = np.linspace(0, w, num_rows)
        print x_coors
        y_coors = np.linspace(0, h, num_cols)
        print y_coors
        for x in x_coors:
            for y in y_coors:
                self._draw_square(dc, x, y, 80)




if __name__ == '__main__':
    app = wx.App(False)
    frame = wx.Frame(None, -1, 'simple')
    view = GameView(frame)
    frame.SetSize(1000, 800)
    frame.view = view
    frame.Show()
    app.MainLoop()


