# -*- coding: utf-8 -*-

"""
This module is for displaying graphics for a cursor task.  This also has functionality for a crosshair.

#############################
Running with queue          #
#############################
This module can be run with a multithread (or multiprocess) Queue.  To run it with a queue, create the object, then run the run_with_queue function, passing in the necessary queue.
An example of this call would be:
        import Queue
        queue = Queue.queue()
        CursorTask.CursorTask().run_with_queue(queue)

To control the graphics, place items in the queue in the format (command, args).  For example:
        queue.put((CursorTask.COLLIDE_LEFT, None))  # This will call the collide left operation with No arguments.
        queue.put((CursorTask.SHOW_LEFT_FLAG, False))  # This will hide our left flag (aka target)

#############################
Running with Keys           #
#############################
This module can be run via the keyboard.  Use in the similar fashion as with the queue, but call the run_with_keys function instead.
            'ESCAPE': quit,
            'LEFT': move left 10 pixels,
            'RIGHT': move right 10 pixels,
            'A': collide left,
            'D': collide right,
            'W': collide Top,
            'S': collide Bottom,

#############################
Crosshairs and blank screen #
#############################
To show the crosshair, call:
    queue.put((CursorTask.SHOW_CROSSHAIR, None))

To show a blank screen, call:
    queue.put((CursorTask.SHOW_BLANK, None))

"""

import pygame
import sys
import os
import queue
from . import PyCrosshair as CCDLCrosshair
import warnings

class CursorTask(CCDLCrosshair.PyCrosshair):

    """
    This class manages a cursor task graphics.  All logic is abstracted -- this is only for displaying items on screen
    for a cursor task.

    terminology:
        the terms target, bar and flag are used interchangeably when referring to the target.
    """

    """
    Commands to put in the queue -  Put in the form
        queue.put((CursorTask.COLLIDE_LEFT, None))     # No arguments -- All commands are in the form of a 2D tuple
        queue.put((CursorTask.SHOW_LEFT_FLAG, False))  # With arguments... hides left target
    """

    # -----------Deprecation Warning!!!---------- #
    warnings.simplefilter('always', DeprecationWarning)
    warnings.warn('This CursorTask has been deprecated! Check out CursorTask.py under the same directory',
                  DeprecationWarning)
    # -----------Deprecation Warning!!!---------- #

    # Collision messages
    COLLIDE_TOP = 'collide_top'
    COLLIDE_BOTTOM = 'collide_bottom'
    COLLIDE_LEFT = 'collide_left'
    COLLIDE_RIGHT = 'collide_right'

    # Uncollide Messages
    UNCOLLIDE_ALL = 'uncollide_all'
    # UNCOLLIDE_LR = 'uncollide_left_right'
    # UNCOLLIDE_TB = 'uncollide_top_bottom'
    UNCOLLIDE_TOP = 'uncollide_right'
    UNCOLLIDE_BOTTOM = 'uncollide_bottom'
    UNCOLLIDE_LEFT = 'uncollide_left'
    UNCOLLIDE_RIGHT = 'uncollide_right'

    # Cursor Task messages
    MOVE_CURSOR = 'move_cursor'
    SHOW_CURSOR = 'show_cursor'
    SHOW_LEFT_FLAG = 'show_left_flag'
    SHOW_RIGHT_FLAG = 'show_right_flag'
    SHOW_TOP_FLAG = 'show_left_flag'
    SHOW_BOTTOM_FLAG = 'show_right_flag'

    # Global settings
    SHOW_BLANK = 'show_blank'
    SHOW_CROSSHAIR = 'show_crosshair'
    SET_CROSSHAIR_CROSS_COLOR = 'set_crosshair_cross_color'
    HIDE_CURSOR = 'hide_cursor'

    CROSSHAIR_BKGRND = 'crosshair_background'
    CURSOR_BKGRND = 'cursor_background'
    CROSSHAIR_CROSS_COLOR_RED = 'crosshair_cross_color_red'
    CROSSHAIR_CROSS_COLOR_WHITE = 'crosshair_cross_color_white'

    # Main Commands:
    ONLY_CROSSHAIR_WITH_BACKGROUND = 'show_only_crosshair_with_background'  # No Args.
    RESET = 'reset_r'

    # Text Commands
    SET_TEXT_DICTIONARY_LIST = 'dictionary_text_list'

    def __init__(self, screen_size_width=1920, screen_size_height=1080, neutral_color=(0, 176, 80), hit_color=(255, 204, 0),
                 crosshair_background_color=(128, 128, 128), cursor_task_background_color=(0, 0, 0), window_x_pos=-1920, window_y_pos=0,
                 target_thickness=200, cursor_radius=60, font_size=60, font_type="Verdana",
                 crosshair_cross_color=(255, 255, 255), show_cursor=False,
                 show_mouse=False, tick_time=10, crosshair_height=30, crosshair_width=30, crosshair_thickness=8,
                 target_size_left=(200, None), target_size_right=(200, None), target_size_top=(None, 100), target_size_bottom=(None, 100), text_dictionary_list=None):
        """
        Defaults to drawing the crosshair first.

        :param screen_size_width:  Width of screen in pixels, defaults to 1920.
        :param screen_size_height: Height of screen in pixels, defaults to 1920.
        :param neutral_color: Color of target when not hit. Specified in (Red, Green, Blue) tuple. Defaults to  (0, 176, 80) -- Greenish blue
        :param hit_color: Color of target when not hit. Specified in (Red, Green, Blue) tuple. Defaults to (0, 176, 80) -- Yellow gold.
        :param crosshair_background_color: Background of crosshair. Defaults to grey.
        :param cursor_task_background_color: Background during cursor task. Defaults to black.
        :param window_x_pos: Position of the window.  Defaults to -1920 (left of primary screen)
        :param window_y_pos: Position of the window.  Defaults to 0 (top of primary screen)
        :param target_thickness: Width of the target bar on the side of the screen.
        :param cursor_radius: Radius of the cursor. Defaults to 60 pixels.
        :param font_size: Size of the font. Defaults to 40.
        :param font_type: Type of the font. Defaults to Calibri (Body)
        :param show_mouse: bool - False hides the mouse, True shows it.  Defaults to false.
        :param tick_time: tick setting for pygame.
        :param crosshair_height: height of crosshair in pixels
        :param crosshair_width: width of crosshair in pixels
        :param crosshair_thickness: thickness of the crosshair in pixels
        :param target_size_left: the size of the left target.  If second dimension is None, we'll set it to the size of the screen height.  First dimension cannot be none.
                                    Defaults to (100, None)
        :param target_size_right: the size of the right target.  If second dimension is None, we'll set it to the size of the screen height.  First dimension cannot be none.
                                    Defaults to (100, None)
        :param target_size_top: the size of the top target.  If first dimension is None, we'll set it to the size of the screen width.  Second dimension cannot be none.
                                    Defaults to (None, 100)
        :param target_size_bottom: the size of the bottom target.  If first dimension is None, we'll set it to the size of the screen width.  Second dimension cannot be none.
                                    Defaults to (None, 100)
        """
        self.screen_width, self.screen_height = screen_size_width, screen_size_height

        self.text_dictionary_list = [] if text_dictionary_list is None else text_dictionary_list

        # Fix our targets (removing all None attributes and replacing with screen height/width.
        self.target_size_left, self.target_size_right, self.target_size_top, self.target_size_bottom = \
            self.fix_none_values_in_target_sizes(target_size_left, target_size_right, target_size_top, target_size_bottom)

        # Set our window position  (not sure if this commands works on non-windows computers...)
        os.environ['SDL_VIDEO_WINDOW_POS'] = str(window_x_pos) + "," + str(window_y_pos)

        self.tick_time = tick_time

        self.neutral_color = neutral_color
        self.hit_color = hit_color

        self.background_color = {self.CROSSHAIR_BKGRND: crosshair_background_color,
                                 self.CURSOR_BKGRND: cursor_task_background_color}
        self.background_color_key = self.CURSOR_BKGRND

        # Init Fields
        self.left_color = self.neutral_color
        self.right_color = self.neutral_color
        self.top_color = self.neutral_color
        self.bottom_color = self.neutral_color

        self.crosshair_height = crosshair_height
        self.crosshair_width = crosshair_width
        self.crosshair_thickness = crosshair_thickness
        self.crosshair_cross_color = crosshair_cross_color

        self.bar_thickness_y = self.screen_width
        self.bar_thickness_x = target_thickness
        self.left_bar_x = 0
        self.right_bar_x = self.screen_width - self.bar_thickness_x

        # Calculate some measures for code readability
        self.left_barrier = self.left_bar_x + self.bar_thickness_x
        self.right_barrier = self.right_bar_x
        self.pixels_to_target = screen_size_width / 2 - self.bar_thickness_x  # Number of pixels we need to move to hit the desired target.

        self.top_y, self.bot_y = 0, self.screen_height - self.bar_thickness_y
        self.cursor_x, self.cursor_y, self.cursor_radius = self.screen_width // 2, self.screen_height // 2, cursor_radius
        self.reset()

        # draw flags
        self.draw_left_flag = True
        self.draw_right_flag = True
        self.draw_top_flag = False
        self.draw_bottom_flag = False

        self.draw_cursor_flag = False

        self.key_actions = {
                            'ESCAPE': self.quit,
                            'UP': lambda: self.move_cursor_delta_y(-10),
                            'DOWN': lambda: self.move_cursor_delta_y(10),
                            'LEFT': lambda: self.move_cursor_delta_x(-10),
                            'RIGHT': lambda: self.move_cursor_delta_x(10),
                            'a': lambda: self.collide_left(),
                            'd': lambda: self.collide_right(),
                            's': lambda: self.collide_bottom(),
                            'w': lambda: self.collide_top(),
                            }

        self.q_action_dictionary = self.gen_action_dictionary()

        # Default of object is to draw the crosshair first.
        self.draw_crosshair_flag = False
        self.draw_cursor_flag = show_cursor

        # Init Pygame
        pygame.init()
        pygame.mouse.set_visible(show_mouse)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.NOFRAME)

        self.font = pygame.font.SysFont(font_type, font_size)
        pygame.event.set_blocked(pygame.MOUSEMOTION)


    def gen_action_dictionary(self):
        """
        This is a function that initializes our action dictionary.

        This is a simple way of encapsulating our function calls.  To use, call:
            action_dictionary[key](args)
        """

        action_dictionary = {self.COLLIDE_LEFT: lambda: self.collide_left(),
                             self.COLLIDE_RIGHT: lambda: self.collide_right(),
                             self.COLLIDE_TOP: lambda: self.collide_top(),
                             self.COLLIDE_BOTTOM: lambda: self.collide_bottom(),
                             # todo fix the rest of these.
                             self.UNCOLLIDE_ALL: lambda: self.uncollide_all(),
                             self.UNCOLLIDE_RIGHT: lambda: self.uncollide_right(),
                             self.UNCOLLIDE_LEFT: lambda: self.uncollide_left(),
                             self.UNCOLLIDE_TOP: lambda: self.uncollide_top(),
                             self.UNCOLLIDE_BOTTOM: lambda: self.uncollide_bottom(),

                             self.MOVE_CURSOR: lambda move_cursor_val: self.set_cursor_x_coord(move_cursor_val),
                             self.SHOW_CURSOR: lambda: self.show_cursor(True),
                             self.HIDE_CURSOR: lambda: self.show_cursor(False),
                             self.SHOW_LEFT_FLAG: lambda booll: self.show_left_flag(booll),
                             self.SHOW_RIGHT_FLAG: lambda boolr: self.show_right_flag(boolr),
                             self.SHOW_BLANK: lambda: self.hide_all(),
                             self.SHOW_CROSSHAIR: lambda scb: self.show_crosshair(scb),
                             self.SET_CROSSHAIR_CROSS_COLOR: lambda color: self.set_crosshairs_color_for_flash(color=color),
                             self.CROSSHAIR_CROSS_COLOR_RED: lambda chred=(255, 0, 0): self.set_crosshairs_color_for_flash(color=chred),
                             self.CROSSHAIR_CROSS_COLOR_WHITE: lambda chwhite=(255, 0, 0): self.set_crosshairs_color_for_flash(color=chwhite),
                             self.ONLY_CROSSHAIR_WITH_BACKGROUND: lambda: self.show_only_crosshairs_with_ch_background(),
                             self.RESET: lambda: self.reset(),
                             self.SET_TEXT_DICTIONARY_LIST: lambda new_text_dictionary_list_l: self.set_text_dictionary_list(new_text_dictionary_list=new_text_dictionary_list_l)}
        return action_dictionary

    def set_text_dictionary_list(self, new_text_dictionary_list):
        if type(new_text_dictionary_list) is dict():
            new_text_dictionary_list = [new_text_dictionary_list]
        self.text_dictionary_list = new_text_dictionary_list

    def fix_none_values_in_target_sizes(self, target_size_left, target_size_right, target_size_top, target_size_bottom):
        """
        top or bottom targets--
            If first dimension is None, converts first dimension to the width of the screen if a top or bottom target.
        left or right targets --
            If second dimension is None, converts second dimension to the height of the screen
        :param target_size_left: tuple, if the second dimension is None, this will change it to the screen height
        :param target_size_right: tuple, if the second dimension is None, this will change it to the screen height
        :param target_size_top: tuple, if the first dimension is None, this will change it to the screen width
        :param target_size_bottom: tuple, if the first dimension is None, this will change it to the screen width
        :return: target_size_left, target_size_right, target_size_top, target_size_bottom -- (unmodified)
        """
        def fix_target_size_lr(original_tuple):
            assert original_tuple[0] is not None
            if original_tuple[1] is None:
                return original_tuple[0], self.screen_height

        def fix_target_size_tb(original_tuple):
            assert original_tuple[1] is not None
            if original_tuple[0] is None:
                return self.screen_width, original_tuple[1]

        target_size_left = fix_target_size_lr(target_size_left)
        target_size_right = fix_target_size_lr(target_size_right)
        target_size_top = fix_target_size_tb(target_size_top)
        target_size_bottom = fix_target_size_tb(target_size_bottom)

        return target_size_left, target_size_right, target_size_top, target_size_bottom


    def reset(self, color=None):
        """
        Resets the cursor to the center and returns the flags back to their neutral color (or color if passed value that is not None)
        :param color: Color to set targets.  Uses neutral color if None. Defaults to None.
        """
        if color is None:
            color = self.neutral_color
        self.cursor_y = self.screen_height // 2
        self.cursor_x = self.screen_width // 2
        self.left_color = color
        self.right_color = color
        self.top_color = color
        self.bottom_color = color

    def set_to_cursor_background_color(self):
        """
        Sets the background to the cursor background color
        """
        self.background_color_key = self.CURSOR_BKGRND

    def set_to_block_game_background(self):
        self.background_color_key = self.CURSOR_BKGRND

    def set_to_crosshair_background_color(self):
        """
        Sets the background to the cursor background color
        """
        self.background_color_key = self.CROSSHAIR_BKGRND

    def quit(self):
        """
        Quits pygame and exits (via sys.exit)
        """
        pygame.quit()
        sys.exit(0)

    def set_cursor_x_coord(self, new_x_position):
        """
        Sets the x position of the cursor to new_x_position
        """
        self.cursor_x = new_x_position

    def set_cursor_y_coord(self, new_y_position):
        """
        Sets the y position of the cursor to new_y_position
        """
        self.cursor_y = new_y_position

    def move_cursor_delta_x(self, delta_x):
        """
        Moves the cursor by delta_x.  Positive for right, negative for left.
        """

        self.cursor_x += delta_x

    def move_cursor_delta_y(self, delta_y):
        """
        Moves the cursor by delta_y.  Positive for down, negative for up.
        """
        self.cursor_y += delta_y

    def collide_left(self, color=None):
        """
        Changes the color of the left flag to the passed color.  If none, uses the default hit color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.left_color = self.hit_color
        else:
            self.left_color = color

    def collide_right(self, color=None):
        """
        Changes the color of the left flag to the passed color.  If none, uses the default hit color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.right_color = self.hit_color
        else:
            self.right_color = color

    def collide_bottom(self, color=None):
        """
        Changes the color of the left flag to the passed color.  If none, uses the default hit color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.bottom_color = self.hit_color
        else:
            self.bottom_color = color

    def collide_top(self, color=None):
        """
        Changes the color of the left flag to the passed color.  If none, uses the default hit color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.top_color = self.hit_color
        else:
            self.top_color = color

    def uncollide_left(self, color=None):
        """
        Changes the color of the left flag to the passed color.  If none, uses the default hit neurtral.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.left_color = self.neutral_color
        else:
            self.left_color = color

    def uncollide_right(self, color=None):
        """
        Changes the color of the left flag to the passed color.  If none, uses the default neutral color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.right_color = self.hit_color
        else:
            self.right_color = color

    def uncollide_top(self, color=None):
        """
        Changes the color of the top flag to the passed color.  If none, uses the default neutral color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.top_color = self.hit_color
        else:
            self.top_color = color

    def uncollide_bottom(self, color=None):
        """
        Changes the color of the bottom flag to the passed color.  If none, uses the default neutral color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.bottom_color = self.hit_color
        else:
            self.bottom_color = color

    def uncollide_all(self, color=None):
        """
        Changes the color of all flags to the passed color.  If None, uses the default neutral color.
        """
        self.uncollide_left(color)
        self.uncollide_right(color)
        self.uncollide_top(color)
        self.uncollide_bottom(color)

    def run_with_keys(self):
        """
        Runs the game with the keyboard.

        Runs infinitely.
        """
        timer = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                # If we get a notification from pygame to quit, do so.
                if event.type == pygame.QUIT:
                    self.quit()
                # If we get a keydown event, handle that event
                if event.type == pygame.KEYDOWN:
                    # Iterate through our key_actions keys.  This is all possible commands we have defined.
                    for action_key in self.key_actions:
                        # Check to see if we have a match to our event
                        if event.key == eval("pygame.K_" + action_key):
                            # We found a match.  Run the command and break out of this loop.
                            self.key_actions[action_key]()
                            break
            # Draw our screen
            self.draw_shapes()
            pygame.display.update()
            timer.tick(self.tick_time)

    def run_with_queue(self, q):
        """
        Runs our game by reading off events off the passed queue. Events should be passed in the form:
            (event, args).
        If no args, pass None instead.
        :param q: Multithread (or multiprocess) object queue to read from.
        :return: None - runs infinitely
        """
        timer = pygame.time.Clock()
        while True:
            self.clear_events()
            try:
                key, args = q.get(False)
                if args is None:
                    self.q_action_dictionary[key]()
                elif key == self.SET_TEXT_DICTIONARY_LIST:
                    self.q_action_dictionary[key](args)
                elif type(args) is not tuple:
                    self.q_action_dictionary[key](args)
                else:
                    self.q_action_dictionary[key](*args)
            except queue.Empty:
                pass
            self.clear_events()
            timer.tick(self.tick_time)
            self.draw_shapes()
            pygame.display.update()

    def show_crosshair(self, b):
        """
        Shows the crosshair
        :return:
        """
        self.draw_crosshair_flag = b

    def show_cursor(self, b):
        """
        Shows the cursor
        """
        self.draw_cursor_flag = b

    def hide_all(self):
        """
        Sets the screen blank, hiding everything
        """
        self.show_cursor(False)
        self.show_all_flags(False)
        self.show_crosshair(False)

    def hide_all_cursor_task_related_items(self):
        self.show_cursor(False)
        self.show_all_flags(False)

    def show_left_flag(self, b):
        """
        B is a bool.  If b, then we show the left flag. Else we hide it.
        :param b: Bool - show the flag or not
        """
        self.draw_left_flag = b

    def show_right_flag(self, b):
        """
        B is a bool.  If b, then we show the right flag. Else we hide it.
        :param b: Bool - show the flag or not
        """
        self.draw_right_flag = b

    def show_top_flag(self, b):
        """
        B is a bool.  If b, then we show the top flag. Else we hide it.
        :param b: Bool - show the flag or not
        """
        self.draw_top_flag = b

    def show_bottom_flag(self, b):
        """
        B is a bool.  If b, then we show the bottom flag. Else we hide it.
        :param b: Bool - show the flag or not
        """
        self.draw_bottom_flag = b

    def show_lr_flags(self, b):
        """
        If b, shows left and right flags.  Else hides left and right flags.
        :param b: bool
        """
        self.show_left_flag(b)
        self.show_right_flag(b)

    def show_tb_flags(self, b):
        """
        If b, shows top and bottom flags.  Else hides top and bottom flags.
        :param b: bool
        """
        self.show_top_flag(b)
        self.show_bottom_flag(b)

    def show_all_flags(self, b):
        """
        Shows all flags (top, bottom, left and right) if b, else hides them all
        :param b: bool
        """
        self.show_lr_flags(b)
        self.show_tb_flags(b)

    def reset_cursor_to_center(self):
        """
        Reset cursor to the center of the screen.
        """
        self.set_cursor_x_coord(int(self.screen_width) // 2)
        self.set_cursor_y_coord(int(self.screen_height) // 2)

    def clear_events(self):
        """
        Clear all events from our pygame event queue.  Needs to be called to prevent freezing
        (maybe due to a pygame bug? simply blocking all events doesn't prevent freezing)
        """
        pygame.event.clear()

    def draw_shapes(self):
        """
        Draws our boards according to how the flags of this class are set.

        This method should not be called externally.

        """

        # Fill the screen with our current background
        self.screen.fill(self.background_color[self.background_color_key])

        if self.draw_crosshair_flag:
            height_half = self.crosshair_height // 2
            width_half = self.crosshair_width // 2
            screenheight_half = self.screen_height // 2
            screenwidth_half = self.screen_width // 2
            pygame.draw.rect(self.screen, self.crosshair_cross_color,
                             pygame.Rect((screenwidth_half - width_half, screenheight_half),
                                         (self.crosshair_width, self.crosshair_thickness)))
            pygame.draw.rect(self.screen, self.crosshair_cross_color,
                             pygame.Rect((screenwidth_half, screenheight_half - height_half),
                                         (self.crosshair_thickness, self.crosshair_height)))

        self.clear_events()

        if self.draw_left_flag:
            # Are we drawing the left flag?
            pygame.draw.rect(self.screen, self.left_color,
                             pygame.Rect((self.left_bar_x, self.top_y), self.target_size_left))
        if self.draw_right_flag:
            # Are we drawing the right flag?
            pygame.draw.rect(self.screen, self.right_color,
                             pygame.Rect((self.right_bar_x, self.top_y), self.target_size_right))

        if self.draw_top_flag:
            # Are we drawing the left flag?
            pygame.draw.rect(self.screen, self.top_color,
                             pygame.Rect((self.left_bar_x, self.top_y), self.target_size_top))
        if self.draw_bottom_flag:
            # Are we drawing the bottom flag?
            pygame.draw.rect(self.screen, self.bottom_color,
                             pygame.Rect((self.right_bar_x, self.bot_y), self.target_size_bottom))

        if self.draw_cursor_flag:
            # Are we showing the cursor?
            pygame.draw.circle(self.screen,
                               (255, 255, 255),
                               [self.cursor_x, self.cursor_y],
                               self.cursor_radius)

        self.draw_text()
        self.clear_events()

    def show_only_crosshairs_with_ch_background(self):
        """
        Shows only the crosshairs, chaning the background color to our background crosshair color
        """
        self.hide_all()
        self.set_to_crosshair_background_color()
        self.show_crosshair(True)

    def show_only_lrtb_flags_with_cursor_background(self, lrtb_lst, show_cursor=False):
        """
        
        :param lrtb_lst: A list containing the elements {'l', 'r', 't', 'b'} that shows whether to show each cursor in the list
                Sets background to the specified cursor background
        :param show_cursor: if True, we'll show the cursor as well, else we'll hide it.
        :return: None
        """
        self.hide_all()
        self.set_to_cursor_background_color()
        lrtb_lst = set([xx.lower() for xx in lrtb_lst])
        if 'l' in lrtb_lst:
            self.show_left_flag(True)
        if 'r' in lrtb_lst:
            self.show_right_flag(True)
        if 't' in lrtb_lst:
            self.show_top_flag(True)
        if 'b' in lrtb_lst:
            self.show_bottom_flag(True)
        if show_cursor:
            self.show_cursor(True)

    def set_crosshairs_color_for_flash(self, color=(255, 255, 255)):
        """
        Sets the crosshair color to color.
        :param color: RGB (tuple) color.  Defaults to white.
        """
        self.crosshair_cross_color = color


    def draw_text(self):
        if type(self.text_dictionary_list) is list:
            for text_dict in self.text_dictionary_list:
                color = text_dict['color']
                x, y= text_dict['pos']
                text = text_dict['text']
                if x is None or y is None:
                    center_x, center_y = self.get_coords_for_message_center(text)
                    x = center_x if x is None else x
                    y = center_y if y is None else y
                answer_txt = self.font.render(text, False, color)
                self.screen.blit(answer_txt, (x, y))

        else:
            text_dict = self.text_dictionary_list
            color = text_dict['color']
            x, y = text_dict['pos']
            text = text_dict['text']
            if x is None or y is None:
                center_x, center_y = self.get_coords_for_message_center(text)
                x = center_x if x is None else x
                y = center_y if y is None else y

            answer_txt = self.font.render(text, False, color)
            self.screen.blit(answer_txt, (x, y))

        size_x, size_y = self.get_message_size('NO')
        no_text_location_x = self.screen_width - self.bar_thickness_x // 2 - size_x // 2
        size_x, size_y = self.get_message_size('YES')
        yes_text_location_x = self.bar_thickness_x // 2 - size_x // 2

        answer_txt = self.font.render('YES', False, (0, 0, 0))
        self.screen.blit(answer_txt, (yes_text_location_x, self.screen_height // 2))

        answer_txt = self.font.render('NO', False, (0, 0, 0))
        self.screen.blit(answer_txt, (no_text_location_x, self.screen_height // 2))

if __name__ == '__main__':
    CursorTask(text_dictionary_list={'text': 'Cat', 'pos': (None, 200), 'color': (255, 200, 255)}).run_with_keys()
