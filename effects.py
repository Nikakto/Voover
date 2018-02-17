from PyQt5.QtCore import QObject, QPoint, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QImage

import math
import random
from functools import wraps


COLOR_MATRIX = {
    0: (255, 0,   0),
    1: (0,   255, 0),
    2: (0,   0,   255),
    3: (0,   255, 255),
    4: (255, 0,   255),
    5: (255, 255, 0),
	6: (0, 200, 255),
	7: (128, 128, 255),
	8: (255, 128, 128),
	9: (128, 255, 128),
}


def black_white(r, g, b):
    if (r + g + b)/3 > 128:
        return 255, 255, 255
    return 0, 0, 0


def blue(r, g, b, factor=0):
    b = b + factor
    if b > 255:
        b = 255
    elif b < 0:
        b = 0
    return r, g, b


def blue_yellow(r, g, b):
    m = (r+g)/2
    return m, m, b


def brightness(r, g, b, factor=0):

    rgb = [r, g, b]
    for index, color in enumerate(rgb):
        color += factor

        if color < 0:
            color = 0
        elif color > 255:
            color = 255

        rgb[index] = color

    return rgb


def colorize(r, g, b, color_matrix=COLOR_MATRIX):

    m = (r+g+b)/3
    color_step = int( math.ceil( 255/(len(color_matrix)-1) ) )

    color_index_not_round = m/color_step
    color_index = int( math.ceil(color_index_not_round) )

    rgb = list(color_matrix[color_index])
    return rgb


def contrast(r, g, b, factor=0):

    factor = (259 * (factor + 255)) / (255 * (259 - factor));

    rgb = [r, g, b]
    for index, color in enumerate(rgb):
        color = factor * (color - 128) + 128

        if color < 0:
            color = 0
        elif color > 255:
            color = 255

        rgb[index] = color

    return rgb


def floodfill(image, color_matrix=COLOR_MATRIX, signal=None):

    def _same_color(rgb_a, rgb_b, sensitive):
        m_a = sum(rgb_a[:3])
        m_b = sum(rgb_b[:3])
        return abs(m_a - m_b) < sensitive/2

    color_step = int(math.ceil(255*3 / (len(color_matrix) - 1)))

    # map of pixels
    pixel_bitmap = [[None] * image.height() for i in range(image.width())]

    # floodfilling
    for i in range(image.width()):

        if signal:
            signal.emit(i)

        if i % 100 == 0:
            print('line: %s/%s' % (i, image.width()))

        for j in range(image.height()):

            if pixel_bitmap[i][j]:
                continue

            floodfill_list = [(i, j)]
            floodfill_color = QColor(image.pixel(i, j)).getRgb()

            r, g, b = COLOR_MATRIX[random.randint(0, len(COLOR_MATRIX)-1)]
            floodfill_by_color = QColor(r, g, b).rgb()

            while floodfill_list:

                _x, _y = floodfill_list.pop()

                my_color = QColor(image.pixel(_x, _y)).getRgb()
                same_color = _same_color(floodfill_color, my_color, color_step)

                if pixel_bitmap[_x][_y] or not same_color:
                    continue

                pixel_bitmap[_x][_y] = floodfill_by_color

                if _x > 0 and pixel_bitmap[_x - 1][_y] is None:
                    floodfill_list.append((_x - 1, _y))

                if _x < image.width()-1 and pixel_bitmap[_x+1][_y] is None:
                    floodfill_list.append((_x+1, _y))

                if _y > 0 and pixel_bitmap[_x][_y - 1] is None:
                    floodfill_list.append((_x, _y - 1))

                if _y < image.height()-1 and pixel_bitmap[_x][_y + 1] is None:
                    floodfill_list.append((_x, _y + 1))

    for i in range(image.width()):
        print('apply color: %s/%s' % (i, image.width()))
        for j in range(image.height()):
            if pixel_bitmap[i][j]:
                image.setPixel(QPoint(i, j), pixel_bitmap[i][j])

    return image


def green(r, g, b, factor=0):
    g = g + factor
    if g > 255:
        g = 255
    elif g < 0:
        g = 0
    return r, g, b


def grey(r, g, b):
    return [(r+g+b)/3] * 3


def invert(r, g, b):
    return 255-r, 255-g, 255-b


def noise(r, g, b, ratio=0.5):

    rgb = [r, g, b]
    for index, color in enumerate(rgb):

        sign = 1 if random.random() > 0.5 else -1
        color = color + color * ratio * random.random() * sign

        if color > 255:
            color = 255
        elif color < 0:
            color = 0

        rgb[index] = color

    return rgb


def red(r, g, b, factor=0):
    r = r + factor
    if r > 255:
        r = 255
    elif r < 0:
        r = 0
    return r, g, b


def sepia(r, g, b, depth=25):

    m = (r+g+b)/3

    r = m + depth*2
    g = m + depth
    b = m

    colors = [r, g, b]
    for index, color in enumerate(colors):
        if color > 255:
            colors[index] = 255

    return colors


class Threader(QObject):

    hack_title = {
        black_white.__name__: 'Black and white image: %p%',
        blue.__name__: 'Blue chanel: %p%',
        blue_yellow.__name__: 'Blue and yellow image: %p%',
        brightness.__name__: 'Brightness: %p%',
        colorize.__name__: 'Fake color: %p%',
        contrast.__name__: 'Contrast: %p%',
        floodfill.__name__: 'Fake color (floodfill): %p%',
        green.__name__: 'Green chanel: %p%',
        grey.__name__: 'Greys: %p%',
        invert.__name__: 'Invert colors: %p%',
        noise.__name__: 'Noize: %p%',
        red.__name__: 'Red chanel: %p%',
        sepia.__name__:  'Sepia: %p%',
    }

    sig_done = pyqtSignal(QImage)
    sig_step = pyqtSignal(int)

    def __init__(self, image, effect, progressbar=None, **kwargs):
        super().__init__()
        self.image = image
        self.effect = effect
        self.kwargs = kwargs

        if progressbar:
            self.progressbar = progressbar
            self.progressbar.setRange(0, self.image.width())

    @pyqtSlot()
    def run(self):
        self.apply_effects()
        self.sig_done.emit(self.image)

    def apply_effect(self, effect, kwargs):

        if self.progressbar:
            self.progressbar.setFormat(self.hack_title.get(effect.__name__, '%p%'))

        if effect.__name__ != floodfill.__name__:
            for i in range(self.image.width()):
                for j in range(self.image.height()):
                    pixel = self.image.pixel(i, j)
                    r, g, b, a = QColor(pixel).getRgb()
                    r, g, b = effect(r, g, b, **kwargs)
                    new_pixel = QColor(r, g, b)
                    self.image.setPixel(QPoint(i, j), new_pixel.rgb())

                # if self.progressbar:
                #     self.progressbar.setValue(i)

                self.sig_step.emit(i)
                if (i+1) % 100 == 0 or i+1 == self.image.width():
                    print('line: %s/%s' % (i+1, self.image.width()))

        else:
            self.image = floodfill(self.image, signal=self.sig_step)

    def apply_effects(self):
        if isinstance(self.effect, (list, tuple)):
            for effect, kwargs in self.effect:
                if effect is not None:
                    self.apply_effect(effect, kwargs)
        else:
            self.apply_effect(self.effect, self.kwargs)