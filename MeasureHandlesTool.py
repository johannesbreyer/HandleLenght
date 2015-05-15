# [h] Show Handles Tool

import os
from math import *

from AppKit import NSImage

from mojo.events import *
from mojo.drawingTools import *
from mojo.extensions import getExtensionDefault, setExtensionDefault

#-----------
# constants
#-----------

#: Handle length in relation to circle radius, for creating circles with Bezier curves.
BEZIER_ARC_CIRCLE = 0.5522847498

#-----------
# functions
#-----------

def vector((x, y), angle, distance):
    """Calculate a new position based on a given angle and distance."""
    _x = x + cos(radians(angle)) * distance
    _y = y + sin(radians(angle)) * distance
    return _x, _y

def get_vector((x1, y1), (x2, y2)):
    """Get the distance and angle between two points."""
    a = x2 - x1
    b = y2 - y1
    distance = sqrt(a ** 2 + b ** 2)
    if a != 0:
        angle_radians = atan(float(b) / a)
        angle_degrees = degrees(angle_radians)
    else:
        angle_degrees = 0
    return distance, angle_degrees

#---------
# objects
#---------

class HandlesMeasures(object):

    draw_box = True
    draw_handles = True
    draw_angles = True

    draw_in = True
    draw_out = True

    radius = 0.5

    font_size = 9
    font = "Lucida Grande Bold"

    stroke_width = 1
    color = 1, 0.5, 0
    stroke_alpha = 0.65

    def __init__(self, glyph):
        self.glyph = glyph

    def draw(self, scale=1.0):
        if self.glyph is not None:
            save()
            fontSize(self.font_size * scale)
            font(self.font)
            if self.draw_box:
                self._draw_box(scale)
            if self.draw_handles:
                self._draw_handles(scale)
            if self.draw_angles:
                self._draw_angles(scale)
            restore()

    def _draw_handles(self, scale):

        d = 0.65

        save()
        fill(*self.color)
        stroke(None)

        for c in self.glyph:
            for bPoint in c.bPoints:
                # get positions
                x0, y0 = bPoint.anchor
                w1, h1 = bPoint.bcpIn
                w2, h2 = bPoint.bcpOut
                x1, y1 = x0 + w1, y0 + h1
                x2, y2 = x0 + w2, y0 + h2
                # draw incoming bcp
                if self.draw_in:
                    if w1 != 0 or h1 != 0:
                        d1 = sqrt(w1 ** 2 + h1 ** 2)
                        d1_caption = '%.2f' % d1
                        text(d1_caption, (x0 + w1 * 0.5, y0 + h1 * d))
                # draw outcoming bcp
                if self.draw_out:
                    if w2 != 0 or h2 != 0:
                        d2 = sqrt(w2 * w2 + h2 * h2)
                        d2_caption = '%.2f' % d2
                        text(d2_caption, (x0 + w2 * 0.5, y0 + h2 * d))
        # done
        restore()

    def _draw_box(self, scale):

        save()
        strokeWidth(self.stroke_width * scale)
        fill(None)
        sw = self.stroke_width * scale * 4
        dashLine(sw, sw)

        for contour in self.glyph:
            for pt in contour.bPoints:
                x0, y0 = pt.anchor
                w1, h1 = pt.bcpIn
                w2, h2 = pt.bcpOut
                x1, y1 = x0 + w1, y0 + h1
                x2, y2 = x0 + w2, y0 + h2

                if self.draw_in and not int(w1) == 0 and not int(h1) == 0:
                    fill(None)
                    c = self.color + (self.stroke_alpha,)
                    stroke(*c)
                    rect(x0, y0, w1, h1)
                    line((x0, y0), (x1, y1))

                    if y1 > y0:
                        y1_ = (y1 + 4) * scale
                    else:
                        y1_ = (y1 - 14) * scale

                    if x1 > x0:
                        x1_ = (x1 + 4) * scale
                    else:
                        x1_ = (x1 - 19) * scale

                    stroke(None)
                    fill(*self.color)
                    text('%.2f' % abs(w1), (x0 + w1 * 0.5, y1_))
                    text('%.2f' % abs(h1), (x1_, y0 + h1 * 0.5))

                if self.draw_out and not int(w2) == 0 and not int(h2) == 0:
                    fill(None)
                    c = self.color + (self.stroke_alpha,)
                    stroke(*c)
                    rect(x0, y0, w2, h2)
                    line((x0, y0), (x2, y2))

                    if y2 > y0:
                        y2_ = (y2 + 4) * scale
                    else:
                        y2_ = (y2 - 14) * scale

                    if x2 > x0:
                        x2_ = (x2 + 4) * scale
                    else:
                        x2_ = (x2 - 19) * scale

                    stroke(None)
                    fill(*self.color)
                    text('%.2f' % abs(x2), (x0 + w2 * 0.5, y2_))
                    text('%.2f' % abs(y2), (x2_, y0 + h2 * 0.5))

        restore()

    def _draw_angles(self, scale):

        d = 0.25
        f = BEZIER_ARC_CIRCLE

        save()

        fill(None)
        strokeWidth(self.stroke_width * scale)
        sw = self.stroke_width * scale * 4
        dashLine(sw, sw)

        for contour in self.glyph:
            for pt in contour.bPoints:

                x0, y0 = pt.anchor
                w1, h1 = pt.bcpIn
                w2, h2 = pt.bcpOut
                x1, y1 = x0 + w1, y0 + h1
                x2, y2 = x0 + w2, y0 + h2

                if self.draw_in and not int(w1) == 0 and not int(h1) == 0:

                    distance, angle = get_vector((x0, y0), (x1, y1))
                    r = distance * d * self.radius

                    if w1 > 0 and h1 > 0:
                        a1 = angle % 90
                        a2 = 90 - a1
                        x3, y3 = vector((x0, y0), angle - a1 * 0.5, distance * d)
                        x4, y4 = vector((x0, y0), angle + a2 * 0.5, distance * d)
                        p1_x, p1_y = x0 + r, y0
                        p2_x, p2_y = x0, y0 + r
                        p3_x, p3_y = p1_x, p1_y + r * f
                        p4_x, p4_y = p2_x + r * f, p2_y

                    elif w1 > 0 and h1 < 0:
                        a1 = angle % 90
                        a2 = 90 - a1
                        x3, y3 = vector((x0, y0), angle - a1 * 0.5, distance * d)
                        x4, y4 = vector((x0, y0), angle + a2 * 0.5, distance * d)
                        p1_x, p1_y = x0 + r, y0
                        p2_x, p2_y = x0, y0 - r
                        p3_x, p3_y = p1_x, p1_y - r * f
                        p4_x, p4_y = p2_x + r * f, p2_y

                    elif w1 < 0 and h1 < 0:
                        a1 = angle % 90
                        a2 = 90 - a1
                        x3, y3 = vector((x0, y0), 180 + angle - a1 * 0.5, distance * d)
                        x4, y4 = vector((x0, y0), 180 + angle + a2 * 0.5, distance * d)
                        p2_x, p2_y = x0 - r, y0
                        p1_x, p1_y = x0, y0 - r
                        p3_x, p3_y = p1_x - r * f, p1_y
                        p4_x, p4_y = p2_x, p2_y - r * f

                    else:
                        a1 = angle % 90
                        a2 = 90 - a1
                        x3, y3 = vector((x0, y0), 180 + angle - a1 * 0.5, distance * d)
                        x4, y4 = vector((x0, y0), 180 + angle + a2 * 0.5, distance * d)
                        p1_x, p1_y = x0 - r, y0
                        p2_x, p2_y = x0, y0 + r
                        p3_x, p3_y = p1_x, p1_y + r * f
                        p4_x, p4_y = p2_x - r * f, p2_y

                    c = self.color + (self.stroke_alpha,)
                    stroke(*c)
                    fill(None)

                    newPath()
                    moveTo((p1_x, p1_y))
                    curveTo((p3_x, p3_y), (p4_x, p4_y), (p2_x, p2_y))
                    drawPath()

                    stroke(None)
                    fill(*self.color)
                    text('%.2f' % a1, (x3, y3))
                    text('%.2f' % a2, (x4, y4))

                if self.draw_out and not int(w2) == 0 and not int(h2) == 0:

                    distance, angle = get_vector((x0, y0), (x2, y2))
                    r = distance * d * self.radius

                    if w2 > 0 and h2 > 0:
                        a1 = angle % 90
                        a2 = 90 - a1
                        x5, y5 = vector((x0, y0), angle - a1 * 0.5, distance * d)
                        x6, y6 = vector((x0, y0), angle + a2 * 0.5, distance * d)
                        p1_x, p1_y = x0 + r, y0
                        p2_x, p2_y = x0, y0 + r
                        p3_x, p3_y = p1_x, p1_y + r * f
                        p4_x, p4_y = p2_x + r * f, p2_y

                    elif w2 > 0 and h2 < 0:
                        a1 = angle % 90
                        a2 = 90 - a1
                        x5, y5 = vector((x0, y0), angle - a1 * 0.5, distance * d)
                        x6, y6 = vector((x0, y0), angle + a2 * 0.5, distance * d)
                        p1_x, p1_y = x0, y0 - r
                        p2_x, p2_y = x0 + r, y0
                        p3_x, p3_y = p1_x + r * f, p1_y
                        p4_x, p4_y = p2_x, p2_y - r * f

                    elif w2 < 0 and h2 < 0:
                        a1 = angle % 90
                        a2 = 90 - a1
                        x5, y5 = vector((x0, y0), 180 + angle - a1 * 0.5, distance * d)
                        x6, y6 = vector((x0, y0), 180 + angle + a2 * 0.5, distance * d)
                        p1_x, p1_y = x0 - r, y0
                        p2_x, p2_y = x0, y0 - r
                        p3_x, p3_y = p1_x, p1_y - r * f
                        p4_x, p4_y = p2_x - r * f, p2_y

                    else:
                        a1 = angle % 90
                        a2 = 90 - a1
                        x5, y5 = vector((x0, y0), 180 + angle - a1 * 0.5, distance * d)
                        x6, y6 = vector((x0, y0), 180 + angle + a2 * 0.5, distance * d)
                        p1_x, p1_y = x0 - r, y0
                        p2_x, p2_y = x0, y0 + r
                        p3_x, p3_y = p1_x, p1_y + r * f
                        p4_x, p4_y = p2_x - r * f, p2_y

                    c = self.color + (self.stroke_alpha,)
                    stroke(*c)
                    fill(None)
                    newPath()
                    moveTo((p1_x, p1_y))
                    curveTo((p3_x, p3_y), (p4_x, p4_y), (p2_x, p2_y))
                    drawPath()

                    stroke(None)
                    fill(*self.color)
                    text('%.2f' % a1, (x5, y5))
                    text('%.2f' % a2, (x6, y6))

        restore()

class MeasureHandlesTool(EditingTool):

    icon_file_name = 'measure-handles-tool-icon.pdf'
    dirname = os.path.dirname(__file__)
    toolbar_icon = NSImage.alloc().initByReferencingFile_(os.path.join(dirname, icon_file_name))

    def setup(self):
        glyph = self.getGlyph()
        self.calculator = HandlesMeasures(glyph)

    def draw(self, scale):
        self.calculator.draw(scale)

    def getToolbarIcon(self):
        return self.toolbar_icon

    def getToolbarTip(self):
        return "Measure Handles Tool"

#--------------
# install tool
#--------------

installTool(MeasureHandlesTool())
