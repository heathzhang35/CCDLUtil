"""
Displays a crosshair using pygame.

#############################
Crosshairs and blank screen #
#############################
To show the crosshair, call:
    show_crosshair()

To show a blank screen, call:
    show_blank
"""

import pygame
import sys
import os
import queue
from CCDLUtil.Utility.Decorators import threaded
from CCDLUtil.Graphics.Util.Decorator import put_call_to_queue


class PyCrosshair(object):

    def __init__(self, screen_size_width=1920, screen_size_height=1080,
                 background_color=(128, 128, 128), window_x_pos=0, window_y_pos=0, cursor_radius=60, font_size=60,
                 font_type="Verdana", rest_crosshair_cross_color=(255, 255, 255),
                 flash_crosshair_cross_color=(255, 0, 0), show_mouse=False, tick_time=10, crosshair_height=60,
                 crosshair_width=60, crosshair_thickness=8, text_dictionary_list=None):
        """
        Defaults to drawing the crosshair first.

        :param screen_size_width:  Width of screen in pixels, defaults to 1920.
        :param screen_size_height: Height of screen in pixels, defaults to 1920.
        :param background_color: Background of crosshair. Defaults to grey.
        :param window_x_pos: Position of the window.  Defaults to -1920 (left of primary screen)
        :param window_y_pos: Position of the window.  Defaults to 0 (top of primary screen)
        :param cursor_radius: Radius of the cursor. Defaults to 60 pixels.
        :param font_size: Size of the font. Defaults to 40.
        :param font_type: Type of the font. Defaults to Calibri (Body)
        :param show_mouse: bool - False hides the mouse, True shows it.  Defaults to false.
        :param tick_time: tick setting for pygame.
        :param crosshair_height: height of crosshair in pixels
        :param crosshair_width: width of crosshair in pixels
        :param crosshair_thickness: thickness of the crosshair in pixels
        """
        # event queue
        self.event_queue = queue.Queue()

        # screen size
        self.screen_width, self.screen_height = screen_size_width, screen_size_height
        self.text_dictionary_list = [] if text_dictionary_list is None else text_dictionary_list

        # Set our window position  (not sure if this commands works on non-windows computers...)
        os.environ['SDL_VIDEO_WINDOW_POS'] = str(window_x_pos) + "," + str(window_y_pos)

        self.tick_time = tick_time
        self.crosshair_height = crosshair_height
        self.crosshair_width = crosshair_width
        self.crosshair_thickness = crosshair_thickness
        self.crosshair_cross_color_default = rest_crosshair_cross_color
        self.crosshair_cross_color_flash = flash_crosshair_cross_color

        # Keep track of the current crosshair color
        self.current_crosshair_cross_color = self.crosshair_cross_color_default
        self.cursor_x, self.cursor_y, self.cursor_radius = self.screen_width//2, self.screen_height//2, cursor_radius

        self.ch_background_color = background_color
        # Default of object is to draw the crosshair first.
        self.draw_crosshair_flag = True

        # Init Pygame
        pygame.init()
        pygame.mouse.set_visible(show_mouse)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.NOFRAME)

        self.font = pygame.font.SysFont(font_type, font_size)
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        # run with queue
        self._run_with_queue()

    @put_call_to_queue
    def reset_crosshair(self):
        """
        Resets our crosshair -- shows crosshair, changes crosshair to default color and hides all texts
        """
        self.text_dictionary_list = []
        self.current_crosshair_cross_color = self.crosshair_cross_color_default
        self.show_crosshair()

    @put_call_to_queue
    def show_crosshair(self):
        """
        Shows the crosshair
        """
        self.draw_crosshair_flag = True

    @put_call_to_queue
    def hide_crosshair(self):
        """
        Hide the crosshair
        """
        self.draw_crosshair_flag = False

    @put_call_to_queue
    def set_crosshairs_color(self, color=(255, 255, 255)):
        """
        Sets the crosshair color to color.
        :param color: RGB (tuple) color.  Defaults to white.
        """
        self.current_crosshair_cross_color = color

    @put_call_to_queue
    def draw_text(self):
        """
        Draws our text contained in text_dictionary_list onscreen.
        :return:
        """
        if type(self.text_dictionary_list) is not list:
            self.text_dictionary_list = [self.text_dictionary_list]
        for text_dict in self.text_dictionary_list:
            assert type(text_dict) is dict
            color = text_dict['color']
            x, y = text_dict['pos']
            text = text_dict['text']
            if x is None or y is None:
                center_x, center_y = self._get_coords_for_message_center(text)
                x = center_x if x is None else x
                y = center_y if y is None else y
            answer_txt = self.font.render(text, False, color)
            self.screen.blit(answer_txt, (x, y))

    @put_call_to_queue
    def blt_text(self, text, x, y, color=(255, 255, 255)):
        """
        Shows text on screen at the passed x and y coords.

        If x is None or Y is none, text will be displayed in the middle of the screen
        :param text: str - text to show
        :param x: x coord. If none, we'll show in center
        :param y: x coord. If none, we'll show in center
        :param color: rgb, defaults to white.
        :return:
        """
        center_x, center_y = self._get_coords_for_message_center(text)
        x = center_x if x is None else x
        y = center_y if y is None else y
        text = self.font.render(text, False, color)
        self.screen.blit(text, (x, y))

    @put_call_to_queue
    def center_multiline_msg(self, msg):
        """
        Displays a multiline message (msg) to screen at the very center of the screen.
        :param msg: The string message
        :return: None - displays to screen
        """
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.font.render(line, False,
                                         (255, 255, 255), (0, 0, 0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (
                self.screen_width// 2 - msgim_center_x,
                self.screen_height// 2 - msgim_center_y + i * 22))

    @put_call_to_queue
    def set_text_dictionary_list(self, new_text_dictionary_list):
        if type(new_text_dictionary_list) is dict():
            new_text_dictionary_list = [new_text_dictionary_list]
        self.text_dictionary_list = new_text_dictionary_list

    @put_call_to_queue
    def quit(self):
        """
        Quits pygame and exits (via sys.exit)
        """
        pygame.quit()
        sys.exit(0)

    # ----------private methods-----------#
    @staticmethod
    def _clear_events():
        """
        Clear all events from our pygame event queue.  Needs to be called to prevent freezing.
        """
        pygame.event.clear()

    @threaded(False)
    def _run_with_queue(self):
        """
        Runs our game by reading off events off the passed queue. Events should be passed in the form:
            (event, args).
        If no args, pass None instead.
        :param q: Multithread (or multiprocess) object queue to read from.
        :return: None - runs infinitely
        """
        timer = pygame.time.Clock()
        while True:
            self._clear_events()
            try:
                self.event_queue.get()
            except queue.Empty:
                pass
            self._clear_events()
            timer.tick(self.tick_time)
            self._draw_shapes()
            pygame.display.update()

    def _draw_shapes(self):
        """
        Draws our boards according to how the flags of this class are set.

        This method should not be called externally.

        """

        # Fill the screen with our current background
        self.screen.fill(self.ch_background_color)

        if self.draw_crosshair_flag:
            height_half = self.crosshair_height // 2
            width_half = self.crosshair_width // 2
            screenheight_half = self.screen_height // 2
            screenwidth_half = self.screen_width // 2

            # The Horizontal Bar of the crosshari
            pygame.draw.rect(self.screen, self.current_crosshair_cross_color,
                             pygame.Rect((screenwidth_half - width_half, screenheight_half - self.crosshair_thickness //
                                          2), (self.crosshair_width, self.crosshair_thickness)))
            # The Vertical Bar
            pygame.draw.rect(self.screen, self.current_crosshair_cross_color,
                             pygame.Rect((screenwidth_half - self.crosshair_thickness // 2, screenheight_half -
                                          height_half), (self.crosshair_thickness, self.crosshair_height)))

        self._clear_events()
        self.draw_text()
        self._clear_events()

    def _get_coords_for_message_center(self, msg):
        """
        Gets the coordinates for centering the message on screen.
        :param msg: The message to center onscreen
        :return: The x y coords to blit the message to have it be at the center of the screen.
        """
        size_x, size_y = self._get_message_size(msg)
        center_x = (self.screen_width // 2) - (size_x // 2)
        center_y = (self.screen_height // 2) - (size_y // 2)
        return center_x, center_y

    def _get_message_size(self, msg):
        """
        Gets the width and height of our message.
        """
        msg_image = self.font.render(msg, False, (255, 255, 255), (0, 0, 0))
        size_x, size_y = msg_image.get_size()
        return size_x, size_y

if __name__ == '__main__':
    ch = PyCrosshair()
    ch.show_crosshair()
    ch.hide_crosshair()