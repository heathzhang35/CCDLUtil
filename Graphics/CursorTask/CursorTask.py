"""
This module is for displaying graphics for a cursor task. It has been re-designed to be more user-friendly and to avoid
multiple queue usage in client's code.

Example:
    ct = CursorTask() # this will create new thread to take function calls off the queue
    ct.<graphic method calls> # client can simply (and logically) call the graphics updating method. It's that easy
"""

import pygame
from . import PyCrosshair as Crosshair
from CCDLUtil.Graphics.Util.Decorator import put_call_to_queue


class CursorTask(Crosshair.PyCrosshair):
    """
    This class manages a cursor task graphics.  All logic is abstracted -- this is only for displaying items on screen
    for a cursor task.

    terminology:
        the terms target, bar and flag are used interchangeably when referring to the target.
    """

    # background command
    CROSSHAIR_BKGRND = 'crosshair_background'
    CURSOR_BKGRND = 'cursor_background'
    # Text Commands
    SET_TEXT_DICTIONARY_LIST = 'dictionary_text_list'

    def __init__(self, screen_size_width=1920, screen_size_height=1080, crosshair_background_color=(128, 128, 128),
                 window_x_pos=-1920, window_y_pos=0, target_thickness=200, cursor_radius=60, font_size=60,
                 font_type="Verdana", rest_crosshair_cross_color=(255, 255, 255),
                 flash_crosshair_cross_color=(255, 0, 0), show_mouse=False, tick_time=10, crosshair_height=60,
                 crosshair_width=60, crosshair_thickness=8, text_dictionary_list=None,
                 show_cursor=False, target_size_left=(200, None), target_size_right=(200, None),
                 target_size_top=(None, 100), target_size_bottom=(None, 100), neutral_color=(0, 176, 80),
                 hit_color=(255, 204, 0), cursor_task_background_color=(0, 0, 0)):
        """
        Defaults to drawing the crosshair first.

        :param screen_size_width:  Width of screen in pixels, defaults to 1920.
        :param screen_size_height: Height of screen in pixels, defaults to 1920.
        :param neutral_color: Color of target when not hit. Specified in (Red, Green, Blue) tuple.
                              Defaults to  (0, 176, 80) -- Greenish blue
        :param hit_color: Color of target when not hit. Specified in (Red, Green, Blue) tuple.
                              Defaults to (0, 176, 80) -- Yellow gold.
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
        :param target_size_left: the size of the left target.  If second dimension is None, we'll set it to the size of
                                 the screen height.  First dimension cannot be none. Defaults to (100, None)
        :param target_size_right: the size of the right target.  If second dimension is None, we'll set it to the size
                                  of the screen height. First dimension cannot be none. Defaults to (100, None)
        :param target_size_top: the size of the top target.  If first dimension is None, we'll set it to the size of the
                                screen width.  Second dimension cannot be none. Defaults to (None, 100)
        :param target_size_bottom: the size of the bottom target.  If first dimension is None, we'll set it to the size
                                   of the screen width.  Second dimension cannot be none. Defaults to (None, 100)
        """
        super(CursorTask, self).__init__(
            screen_size_width=screen_size_width, screen_size_height=screen_size_height,
            background_color=crosshair_background_color, window_x_pos=window_x_pos, window_y_pos=window_y_pos,
            cursor_radius=cursor_radius, font_size=font_size, font_type=font_type,
            rest_crosshair_cross_color=rest_crosshair_cross_color,
            flash_crosshair_cross_color=flash_crosshair_cross_color, show_mouse=show_mouse, tick_time=tick_time,
            crosshair_height=crosshair_height, crosshair_width=crosshair_width, crosshair_thickness=crosshair_thickness,
            text_dictionary_list=text_dictionary_list)

        # Fix our targets (removing all None attributes and replacing with screen height/width.
        self.target_size_left, self.target_size_right, self.target_size_top, self.target_size_bottom = \
            self._fix_none_values_in_target_sizes(target_size_left, target_size_right, target_size_top,
                                                     target_size_bottom)
        self.crosshair_cross_color = rest_crosshair_cross_color

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

        self.bar_thickness_y = self.screen_width
        self.bar_thickness_x = target_thickness
        self.left_bar_x = 0
        self.right_bar_x = self.screen_width - self.bar_thickness_x

        # Calculate some measures for code readability
        self.left_barrier = self.left_bar_x + self.bar_thickness_x
        self.right_barrier = self.right_bar_x
        # Number of pixels we need to move to hit the desired target.
        self.pixels_to_target = screen_size_width / 2 - self.bar_thickness_x

        self.top_y, self.bot_y = 0, self.screen_height - self.bar_thickness_y
        self.reset_cursor()

        # draw flags
        self.draw_left_flag = True
        self.draw_right_flag = True
        self.draw_top_flag = False
        self.draw_bottom_flag = False
        self.draw_cursor_flag = False

        self.draw_yes_flag = True
        self.draw_no_flag = True

        # Default of object is to draw the crosshair first.
        self.draw_cursor_flag = show_cursor

    # ----------Following are graphic methods that users call---------- #

    @put_call_to_queue
    def reset_cursor(self, color=None):
        """
        Resets the cursor to the center and returns the flags back to their neutral color (or color if passed value that
        is not None)
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

    @put_call_to_queue
    def set_to_cursor_background_color(self):
        """
        Sets the background to the cursor background color
        """
        self.background_color_key = self.CURSOR_BKGRND

    @put_call_to_queue
    def set_to_block_game_background(self):
        self.background_color_key = self.CURSOR_BKGRND

    @put_call_to_queue
    def set_to_crosshair_background_color(self):
        """
        Sets the background to the cursor background color
        """
        self.background_color_key = self.CROSSHAIR_BKGRND

    @put_call_to_queue
    def set_cursor_x_coord(self, new_x_position):
        """
        Sets the x position of the cursor to new_x_position
        """
        self.cursor_x = new_x_position

    @put_call_to_queue
    def set_cursor_y_coord(self, new_y_position):
        """
        Sets the y position of the cursor to new_y_position
        """
        self.cursor_y = new_y_position

    @put_call_to_queue
    def move_cursor_delta_x(self, delta_x):
        """
        Moves the cursor by delta_x.  Positive for right, negative for left.
        """

        self.cursor_x += delta_x

    @put_call_to_queue
    def move_cursor_delta_y(self, delta_y):
        """
        Moves the cursor by delta_y.  Positive for down, negative for up.
        """
        self.cursor_y += delta_y

    @put_call_to_queue
    def collide_left(self, color=None):
        """
        Changes the color of the left flag to the passed color.  If none, uses the default hit color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.left_color = self.hit_color
        else:
            self.left_color = color

    @put_call_to_queue
    def collide_right(self, color=None):
        """
        Changes the color of the left flag to the passed color.  If none, uses the default hit color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.right_color = self.hit_color
        else:
            self.right_color = color

    @put_call_to_queue
    def collide_bottom(self, color=None):
        """
        Changes the color of the left flag to the passed color.  If none, uses the default hit color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.bottom_color = self.hit_color
        else:
            self.bottom_color = color

    @put_call_to_queue
    def collide_top(self, color=None):
        """
        Changes the color of the left flag to the passed color.  If none, uses the default hit color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.top_color = self.hit_color
        else:
            self.top_color = color

    @put_call_to_queue
    def uncollide_left(self, color=None):
        """
        Changes the color of the left flag to the passed color.  If none, uses the default hit neurtral.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.left_color = self.neutral_color
        else:
            self.left_color = color

    @put_call_to_queue
    def uncollide_right(self, color=None):
        """
        Changes the color of the left flag to the passed color.  If none, uses the default neutral color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.right_color = self.hit_color
        else:
            self.right_color = color

    @put_call_to_queue
    def uncollide_top(self, color=None):
        """
        Changes the color of the top flag to the passed color.  If none, uses the default neutral color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.top_color = self.hit_color
        else:
            self.top_color = color

    @put_call_to_queue
    def uncollide_bottom(self, color=None):
        """
        Changes the color of the bottom flag to the passed color.  If none, uses the default neutral color.

        :param color: rgb color (tuple)
        """
        if color is None:
            self.bottom_color = self.hit_color
        else:
            self.bottom_color = color

    @put_call_to_queue
    def uncollide_all(self, color=None):
        """
        Changes the color of all flags to the passed color.  If None, uses the default neutral color.
        """
        self.uncollide_left(color)
        self.uncollide_right(color)
        self.uncollide_top(color)
        self.uncollide_bottom(color)

    @put_call_to_queue
    def show_cursor(self):
        """
        Shows the cursor
        """
        self.draw_cursor_flag = True

    @put_call_to_queue
    def hide_cursor(self):
        self.draw_cursor_flag = False

    @put_call_to_queue
    def show_left_flag(self):
        """
        """
        self.draw_left_flag = True

    @put_call_to_queue
    def hide_left_flag(self):
        """
        """
        self.draw_left_flag = False

    @put_call_to_queue
    def show_right_flag(self):
        """
        """
        self.draw_right_flag = True

    @put_call_to_queue
    def hide_right_flag(self):
        """
        """
        self.draw_right_flag = False

    @put_call_to_queue
    def show_top_flag(self):
        """
        """
        self.draw_top_flag = True

    @put_call_to_queue
    def hide_top_flag(self):
        """
        """
        self.draw_top_flag = False

    @put_call_to_queue
    def show_bottom_flag(self):
        """
        """
        self.draw_bottom_flag = True

    @put_call_to_queue
    def hide_bottom_flag(self):
        """
        """
        self.draw_bottom_flag = False

    @put_call_to_queue
    def show_yes_flag(self):
        """
        """
        self.draw_yes_flag = True

    @put_call_to_queue
    def hide_yes_flag(self):
        """
        """
        self.draw_yes_flag = False

    @put_call_to_queue
    def show_no_flag(self):
        """
        """
        self.draw_no_flag = True

    @put_call_to_queue
    def hide_no_flag(self):
        """
        """
        self.draw_no_flag = False

    @put_call_to_queue
    def show_lr_flags(self):
        """
        """
        self.show_left_flag()
        self.show_right_flag()

    @put_call_to_queue
    def hide_lr_flags(self):
        """
        """
        self.hide_left_flag()
        self.hide_right_flag()

    @put_call_to_queue
    def show_tb_flags(self):
        """
        """
        self.show_top_flag()
        self.show_bottom_flag()

    @put_call_to_queue
    def hide_tb_flags(self):
        """
        """
        self.hide_top_flag()
        self.hide_bottom_flag()

    @put_call_to_queue
    def show_all_flags(self):
        """
        """
        self.show_lr_flags()
        self.show_tb_flags()

    @put_call_to_queue
    def hide_all_flags(self):
        """
        """
        self.hide_lr_flags()
        self.hide_tb_flags()

    @put_call_to_queue
    def show_all(self):
        """
        Sets the screen blank, hiding everything
        """
        super(CursorTask, self).show_crosshair()
        self.show_yes_flag()
        self.show_no_flag()
        self.show_cursor()
        self.show_all_flags()

    @put_call_to_queue
    def hide_all(self):
        """
        Sets the screen blank, hiding everything
        """
        super(CursorTask, self).hide_crosshair()
        self.hide_yes_flag()
        self.hide_no_flag()
        self.hide_cursor()
        self.hide_all_flags()

    @put_call_to_queue
    def reset_cursor_to_center(self):
        """
        Reset cursor to the center of the screen.
        """
        self.set_cursor_x_coord(int(self.screen_width) // 2)
        self.set_cursor_y_coord(int(self.screen_height) // 2)

    @put_call_to_queue
    def show_only_crosshairs_with_ch_background(self):
        """
        Shows only the crosshairs, changing the background color to our background crosshair color
        """
        self.hide_all()
        self.set_to_crosshair_background_color()
        self.show_crosshair()

    @put_call_to_queue
    def show_only_lrtb_flags_with_cursor_background(self, lrtb_lst, show_cursor=False):
        """
        Sets background to the specified cursor background

        :param lrtb_lst: A list containing the elements {'l', 'r', 't', 'b'} that shows whether to show each cursor in
        the list
        :param show_cursor: if True, we'll show the cursor as well, else we'll hide it.
        :return: None
        """
        self.hide_all()
        self.set_to_cursor_background_color()
        lrtb_lst = set([xx.lower() for xx in lrtb_lst])
        if 'l' in lrtb_lst:
            self.show_left_flag()
        if 'r' in lrtb_lst:
            self.show_right_flag()
        if 't' in lrtb_lst:
            self.show_top_flag()
        if 'b' in lrtb_lst:
            self.show_bottom_flag()
        if show_cursor:
            self.show_cursor()

    @put_call_to_queue
    def draw_text(self):
        if type(self.text_dictionary_list) is list:
            for text_dict in self.text_dictionary_list:
                color = text_dict['color']
                x, y = text_dict['pos']
                text = text_dict['text']
                if x is None or y is None:
                    center_x, center_y = self._get_coords_for_message_center(text)
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
                center_x, center_y = self._get_coords_for_message_center(text)
                x = center_x if x is None else x
                y = center_y if y is None else y

            answer_txt = self.font.render(text, False, color)
            self.screen.blit(answer_txt, (x, y))

        size_x, size_y = self._get_message_size('NO')
        no_text_location_x = self.screen_width - self.bar_thickness_x // 2 - size_x // 2
        size_x, size_y = self._get_message_size('YES')
        yes_text_location_x = self.bar_thickness_x // 2 - size_x // 2

        answer_txt = self.font.render('YES', False, (0, 0, 0))
        if self.draw_yes_flag:
            self.screen.blit(answer_txt, (yes_text_location_x, self.screen_height // 2))

        answer_txt = self.font.render('NO', False, (0, 0, 0))
        if self.draw_no_flag:
            self.screen.blit(answer_txt, (no_text_location_x, self.screen_height // 2))

    # ----------private methods---------- #
    def _draw_shapes(self):
        """
        Draws our boards according to how the flags of this class are set.

        This method should not be called externally.

        """

        # Fill the screen with our current background
        self.screen.fill(self.background_color[self.background_color_key])

        super(CursorTask, self)._draw_shapes()
        CursorTask._clear_events()

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
        CursorTask._clear_events()

    def _fix_none_values_in_target_sizes(self, target_size_left, target_size_right, target_size_top,
                                         target_size_bottom):
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

if __name__ == '__main__':
    ct = CursorTask(text_dictionary_list={'text': 'Cat', 'pos': (None, 200), 'color': (255, 200, 255)},
                    window_x_pos=-1920, screen_size_width=1680, screen_size_height=1050)
    ct.show_right_flag()
    ct.show_bottom_flag()
