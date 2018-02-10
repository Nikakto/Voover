from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton, QLabel, QSlider, QTabWidget, QHBoxLayout, QVBoxLayout, QWidget

from functools import partial

import effects


class BrightContrastWidget(QWidget):

    def __init__(self, label_widget=None):

        super(QWidget, self).__init__()

        self.widgetBrightness = TitledSliderWidget("Brightness", label_widget, TitledSliderWidget.slider_brightness)
        self.widgetContrast = TitledSliderWidget("Contrast", label_widget, TitledSliderWidget.slider_contrast)

        # sliders layout
        self.layout = QVBoxLayout()

        self.layout.addStretch(1)
        self.layout.addWidget(self.widgetBrightness)
        self.layout.addStretch(1)
        self.layout.addWidget(self.widgetContrast)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

    def apply(self):
        self.widgetBrightness.apply()
        self.widgetContrast.apply()

    def reset(self):
        self.widgetBrightness.reset()
        self.widgetContrast.reset()


class RGBWidget(QWidget):

    def __init__(self, label_widget=None):

        super(QWidget, self).__init__()

        self.widgetRed = TitledSliderWidget("Red", label_widget, TitledSliderWidget.slider_red)
        self.widgetGreen = TitledSliderWidget("Green", label_widget, TitledSliderWidget.slider_green)
        self.widgetBlue = TitledSliderWidget("Blue", label_widget, TitledSliderWidget.slider_blue)

        # sliders layout
        self.layout = QVBoxLayout()

        self.layout.addStretch(1)
        self.layout.addWidget(self.widgetRed)
        self.layout.addStretch(1)
        self.layout.addWidget(self.widgetGreen)
        self.layout.addStretch(1)
        self.layout.addWidget(self.widgetBlue)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

    def apply(self):
        self.widgetRed.apply()
        self.widgetGreen.apply()
        self.widgetBlue.apply()

    def reset(self):
        self.widgetRed.reset()
        self.widgetGreen.reset()
        self.widgetBlue.reset()


class SliderTabsWidget(QTabWidget):

    def __init__(self, label_widget=None):

        super(QTabWidget, self).__init__()

        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tab_bc = BrightContrastWidget(label_widget)
        self.tab_rgb = RGBWidget(label_widget)

        self.tabs.addTab(self.tab_bc, "Brightness / Contrast")
        self.tabs.addTab(self.tab_rgb, "RGB")
        self.layout.addWidget(self.tabs)

        self.layout_buttons = QHBoxLayout()

        self.layout_buttons.addStretch(1)

        self.button_apply = QPushButton()
        self.button_apply.setText('Apply')
        self.button_apply.setFixedWidth(100)
        self.button_apply.clicked.connect(self.apply)
        self.layout_buttons.addWidget(self.button_apply)

        self.button_reset = QPushButton()
        self.button_reset.setText('Reset')
        self.button_reset.setFixedWidth(100)
        self.button_reset.clicked.connect(self.reset)
        self.layout_buttons.addWidget(self.button_reset)

        self.layout.addLayout(self.layout_buttons)

        self.setLayout(self.layout)
        self.setFixedHeight(300)

    def apply(self):
        self.tab_bc.apply()
        self.tab_rgb.apply()
        self.reset()

    def reset(self):
        self.tab_bc.reset()
        self.tab_rgb.reset()


class TitledSliderWidget(QWidget):
    
    def __init__(self, title="Unnamed", label_widget=None, action=None):

        super(QWidget, self).__init__()

        self.action = action
        self.old_value = 0
        self.layout = QVBoxLayout()
        self.imageLabel = label_widget

        self.label = QLabel(title)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
    
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(25)
        self.slider.setSingleStep(0)
        self.slider.setValue(50)

        self.layout.addWidget(self.slider)

        self.setLayout(self.layout)

    def effect(self, effect, **kwargs):
        image = self.imageLabel.pixmap().toImage()
        image = effect(image, **kwargs)
        pixmap = QPixmap.fromImage(image)
        self.imageLabel.setPixmap(pixmap)

    def apply(self):
        if self.action:
            self.action(self)   # WTF???

    def reset(self):
        self.old_value = 0
        self.slider.setValue(50)


    def slider_blue(self):

        blue = self.slider.value() - 50 - self.old_value
        if blue != 0:
            self.old_value += blue
            self.effect(effects.blue, factor=blue)


    def slider_brightness(self):

        brightness = (self.slider.value() - 50) * 1.5 - self.old_value
        if brightness != 0:
            self.old_value += brightness
            self.effect(effects.brightness, factor=brightness)

    def slider_contrast(self):

        contrast = self.slider.value() - 50 - self.old_value
        if contrast != 0:
            self.old_value += contrast
            self.effect(effects.contrast, factor=contrast)

    def slider_green(self):

        green = self.slider.value() - 50 - self.old_value
        if green != 0:
            self.old_value += green
            self.effect(effects.green, factor=green)

    def slider_red(self):

        red = self.slider.value() - 50 - self.old_value
        if red != 0:
            self.old_value += red
            self.effect(effects.red, factor=red)