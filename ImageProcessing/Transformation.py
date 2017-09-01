"""
For functions related to scaling and transforming images.
"""
import wx

def scale_bitmap(bitmap, width, height):
    """
    Rescales a bitmap to the given width and height
    :param bitmap: unscaled bitmatp
    :param width: new width in pixels
    :param height: new height in pixels
    :return: new scaled bitmat
    """
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result
